# 12 · Exportar y publicar

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 12 de 12 · **FIN DE LA SERIE**

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=yDH_1WFARm8> |
| **Duración** | 11 min 21 s |
| **Publicado** | 1 de febrero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Plataforma** | itch.io (también válido para Steam) |

El capítulo final: sacar el juego de tu ordenador y ponerlo en manos de la gente. El
autor ha publicado en **itch.io** y también en **Steam**, y asegura que el proceso por
el lado de GameMaker es **prácticamente idéntico**.

## Índice de contenido

1. Elegir la plataforma de destino
2. La advertencia sobre HTML5
3. Ajustes de la plataforma
4. Crear el ejecutable
5. itch.io: crear el proyecto
6. Subir el archivo y ajustar el reproductor
7. Clasificación, género y etiquetas
8. Visibilidad: trabajar en borrador
9. Depurar el fallo de la cámara en HTML5
10. Personalizar la página
11. Publicar

---

## 1. Elegir la plataforma de destino

Arriba verás el indicador de **Current Build Target** (por ejemplo, *Windows*).

- Para publicar en **Steam** o subir un juego descargable a itch.io, **Windows** es
  perfectamente válido.
- Si quieres un **juego de navegador**, necesitas **HTML5**. Para eso hay que **iniciar
  sesión con tu cuenta de YoYo/GameMaker** desde el botón correspondiente, lo que te
  permite descargar ese módulo de plataforma.

El autor elige **HTML5** para este tutorial, y lo prueba ejecutando el juego.

---

## 2. La advertencia sobre HTML5

> **Los juegos HTML5 se comportan de forma ligeramente distinta** a las compilaciones de
> prueba. Puede que necesites retoques y soluciones alternativas. Es la naturaleza de la
> bestia.

De ahí la recomendación más importante del capítulo:

> **No construyas el juego entero y decidas al final que será de navegador.** Decide
> desde el principio si lo será, y **pruébalo así constantemente** durante todo el
> desarrollo.

---

## 3. Ajustes de la plataforma

Antes de exportar, pulsa **Create Executable → Game Settings** y baja hasta la sección
de la plataforma. Allí puedes cambiar:

- El **título** que aparecerá en la pestaña del navegador.
- Las **imágenes** del juego.
- Otros ajustes de la plataforma.

El autor hace dos cosas:

1. **Desmarcar «Interpolate colors between pixels»** (por costumbre, para que el pixel
   art no se vea borroso).
2. Cambiar el título del navegador a **`Test Game for Tutorial`**.

Después: **Apply** y **OK**.

---

## 4. Crear el ejecutable

Pulsa **Create Executable**. Te dará dos opciones:

| Opción | Cuándo |
|---|---|
| **Loose Files** | Archivos sueltos |
| **Zip** | Un único archivo comprimido |

> Elige **Zip**, que es lo que acepta itch.io.

Guárdalo siguiendo la **convención de nombres de todo el curso**:

```
GM Tutorial 260119 V1
```

Guárdalo en el escritorio. Verás la barra de progreso: *está construyendo*. Al
terminar se abrirá la carpeta; ciérrala. Ya tienes el juego en tu escritorio.

---

## 5. itch.io: crear el proyecto

1. Entra en **itch.io** con tu cuenta.
2. Despliega tu menú y ve al **Dashboard**.
3. Pulsa **New project**.

Rellena la información:

| Campo | Valor de ejemplo |
|---|---|
| **Title** | `Test Tutorial for Publishing` |
| **URL** | Puede ser **distinta** del título |
| **Description** | La descripción del juego |
| **Classification** | `Game` |
| **Kind of project** | `HTML5` (o *Downloadable* si subes un ejecutable) |
| **Release status** | `In development` |
| **Payments** | `No payments` (o configúralo si vas a cobrar) |

---

## 6. Subir el archivo y ajustar el reproductor

En **Uploads**, sube tu archivo `.zip` (por ejemplo `GM Tutorial 260119 version one`) y
marca:

- **«This file will be played in the browser»**.

Opciones de visualización que elige el autor:

| Opción | Valor | Motivo |
|---|---|---|
| Embebido en la página | Sí | |
| Tamaño | **Manual: 960 × 540** | La cámara es de 480 × 270, pero `rSplash` estira la ventana al doble |
| Mobile friendly | No | |
| Automatically start | No | No le gusta que arranque solo |
| Fullscreen button | No | |
| Enable scroll bars | No | |

> Para **sustituir** el archivo: borra el anterior y sube el nuevo. Puedes borrarlo
> cuando quieras.

---

## 7. Clasificación, género y etiquetas

En la sección *More details & description*:

- **Description:** el texto completo de la página del juego.
- **Genre:** por ejemplo `Action`.
- **Tags:** `2D`, `Pixel Art`, `Indie`… elige los que encajen.
- **App store links:** si también está en tiendas.
- **Custom noun:** si no quieres que se llame «game» puedes poner otro sustantivo.
- **Comments:** actívalos o desactívalos a tu gusto.

> El autor marca explícitamente la casilla de que **el proyecto no contiene resultados
> de IA generativa**, añadiendo —en sus propias palabras— que eso «es de perdedores».

---

## 8. Visibilidad: trabajar en borrador

> **Mantén el proyecto en `Draft` mientras editas y pruebas.** Así **nadie puede
> encontrarlo excepto tú**, y puedes experimentar con tranquilidad.

Pulsa **Save & view page** para ver el resultado.

---

## 9. Depurar el fallo de la cámara en HTML5

Al ver la página aparece de inmediato **un problema gráfico en el menú principal**.

Diagnóstico del autor:

> El objeto cámara es lo que mantiene la coherencia visual entre las distintas rooms.
> **Pero en la room del título no hay ninguna cámara habilitada.**

 Solución:

1. Abre `rTitle`.
2. **Enable Viewports.**
3. **Viewport 0 → Visible.**
4. Vuelve a **Create Executable → Package zip**, esta vez como **V2**.
5. En itch.io, **borra el archivo antiguo** y sube el nuevo.

> «Me alegro de que haya pasado, porque quería mostraros que **esto puede ocurrir,
> especialmente con juegos de navegador**. Si fuera un juego de Windows funcionaría
> exactamente igual que al probarlo. Los juegos de navegador exigen prestar atención a
> ciertos detalles.»

Al recargar la página, el juego funciona como se esperaba.

---

## 10. Personalizar la página

Desde **Edit theme** puedes cambiar por completo el aspecto:

- **Color de fondo** (el autor prueba un morado oscuro).
- **Color secundario** (un rosa claro).
- **Tipografía** y otros elementos.
- **Banner** e imagen de fondo.

Y desde **Edit game** puedes añadir:

| Elemento | Recomendación |
|---|---|
| **Cover image** | **630 × 500** |
| **Screenshots** | Capturas del juego |
| **Trailer** | Vídeo de YouTube o Vimeo |
| **Imágenes** | Para el cuerpo de la página |

Para la portada, el consejo es simple: crea una imagen de **630 × 500**, mete una
captura del juego y añade el título.

> **No olvides pulsar «Save»** después de cada cambio.

---

## 11. Publicar

Cuando estés listo:

1. Vuelve al **Dashboard** y pulsa **Edit**.
2. Cambia la visibilidad de `Draft` a **`Restricted`** o **`Public`**.
3. Pulsa **Save**.

Ya está publicado. Y **puedes volver a ponerlo en borrador** cuando quieras.

> El autor insiste en la disciplina: **déjalo en borrador mientras editas y pruebas**,
> para que nadie lo encuentre hasta que esté listo.

---

## Puntos clave

1. **Elige la plataforma de destino** al principio: Windows/Mac para descargable,
   **HTML5** (con cuenta de GameMaker) para navegador.
2. **Nunca dejes HTML5 para el final.** Decídelo desde el día uno y prueba así durante
   todo el desarrollo.
3. **Desmarca «Interpolate colors between pixels»** en los ajustes de la plataforma si
   haces pixel art.
4. **Exporta en Zip**, que es lo que acepta itch.io.
5. **Sigue la convención de nombres** `Proyecto AAMMDD Vn` también en los ejecutables.
6. **Elige el tamaño del reproductor a mano** para que coincida con el de tu ventana
   real (960 × 540 en este proyecto).
7. **Mantén el proyecto en `Draft`** mientras pruebas: nadie lo verá.
8. **Toda room visible necesita su cámara habilitada**; si no, se rompe la coherencia
   visual entre habitaciones.
9. **Para actualizar**: borra el archivo antiguo y sube el nuevo con una versión
   superior.
10. **Portada de 630 × 500**, y añade capturas y tráiler para que la página luzca
    profesional.
11. **Publicar es cambiar la visibilidad a Public y guardar.** Puedes revertirlo.

---

## Ejercicio propuesto

> **Objetivo:** publicar tu juego por primera vez, con una página decente, y aprender a
> iterar sobre una versión ya subida.

1. Decide **ahora** si tu juego será de navegador o descargable, y configura la
   plataforma de destino en consecuencia.
2. Entra en **Game Settings → Platform** y pon el título de la pestaña del navegador
   con el nombre real de tu juego. Desmarca la interpolación de píxeles.
3. Exporta con **Create Executable → Zip** como `TuJuego <AAMMDD> V1` en el escritorio.
4. Crea una cuenta en **itch.io** si no la tienes y pulsa **New project**.
5. Rellena título, URL, descripción, clasificación (`Game`) y tipo de proyecto.
6. Sube el `.zip`, marca *played in the browser* y configura el reproductor: embebido,
   **tamaño manual** igual al de tu ventana, y desactiva autoarranque, pantalla completa
   y barras de scroll.
7. Pon género y al menos tres etiquetas (por ejemplo `2D`, `Pixel Art`, `Indie`).
8. **Déjalo en `Draft`** y pulsa *Save & view page*.
9. Comprueba **todas** las rooms: título, juego cenital y plataformas. Si alguna se ve
   mal, revisa que tenga **Enable Viewports** y **Viewport 0 Visible**.
10. Corrige lo que falle, exporta como **V2**, borra el archivo antiguo en itch.io y
    sube el nuevo.
11. Crea una **portada de 630 × 500** con una captura y el título, súbela, y añade al
    menos dos **capturas de pantalla**.
12. Personaliza el tema con tus propios colores.
13. Cuando estés conforme, pon la visibilidad en **Public** y guarda.

**Reto extra:** vuelve a poner el proyecto en borrador, cambia algo del juego (por
ejemplo el color del barco o la velocidad de disparo), exporta como **V3** y actualiza
el archivo en itch.io. Comprueba que la página refleja los cambios y reflexiona sobre lo
rápido que es iterar cuando el pipeline ya está montado.
