# 07 · Los eventos de GameMaker, en vídeo y en español — transcripción estructurada

> **Fuente:** [*Introducción a los EVENTOS [Game Maker 2024]*](https://youtu.be/tPUNtpHVFSw)
> de [Altair_AML](https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw) · **16 min 17 s** · 26-03-2024.
>
> El compañero natural de [`06 · Curso de GML`](./06%20-%20Curso%20de%20GML%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md):
> aquel explica el lenguaje, este explica **cuándo se ejecuta tu código**, que es la fuente del
> 80 % de los bugs de principiante.
>
> ⚠️ **Anotaciones de 2026 marcadas con 🔺.**

---

*«Los eventos, en términos muy simples, son solo un momento en el que se va a ejecutar el
código. Puede ser solo una vez, puede ser constantemente o puede ser por una alarma.»*

---

## 1. Create

**Se ejecuta una vez, cuando la instancia entra en la room.**

Es donde se asignan las variables y todo lo que solo deba pasar una vez.

> ⚠️ **La trampa que señala el autor, y es real:** *«Los objetos en el cuarto se crean **en
> orden**. Si en el Create tienes un código que llama a otro objeto que aún no se ha creado,
> puede ocurrir un error por no encontrarlo.»*
>
> 🔺 **Cómo se evita en 2026:** usa un objeto controlador con **profundidad de creación** más
> alta, o mueve la dependencia al evento **Room Start**, que se ejecuta cuando ya existen todas
> las instancias.

---

## 2. Destroy

**Se ejecuta cuando la instancia deja la room**, normalmente por `instance_destroy()`.

> *«Se usa cuando quieres lanzar una partícula de un enemigo al destruirlo, o que suelte
> items.»*

```gml
// Destroy de obj_enemigo
repeat (12) instance_create_layer(x, y, "Efectos", obj_chispa);
if (irandom(100) < 20) instance_create_layer(x, y, "Instances", obj_botiquin);
```

---

## 3. Clean Up

Se ejecuta en **tres momentos**: al cambiar de room, al terminar el juego y al destruirse la
instancia.

> *«Se usa generalmente para liberar espacio con funciones surface o funciones de buffer.»*

```gml
// Clean Up
if (surface_exists(surf)) surface_free(surf);
if (buffer_exists(buf))   buffer_delete(buf);
```

> 🔺 **Esto es más importante de lo que el vídeo sugiere.** Structs y arrays se limpian solos,
> pero **superficies, buffers, estructuras `ds_*`, sistemas de partículas y time sources no**.
> Si no los liberas aquí, tienes una fuga de memoria.
> Ver [`01 - Fundamentos/15 · Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md).

---

## 4. Step — el evento central

*«Es uno de los más importantes, ya que aquí va la mayoría del código: movimiento, habilidades,
inteligencia. Se ejecuta constantemente, como en un bucle.»*

Se divide en tres:

| Evento | Cuándo |
|---|---|
| **Begin Step** | Antes del Step normal de todas las instancias |
| **Step** | El normal. **Es el que vas a usar el 95 % de las veces** |
| **End Step** | Después |

> *«La diferencia es que uno se ejecuta un poco antes y el otro un poco después. Son escasas
> esas veces, así que generalmente vamos a usar el Step normal.»*

🔺 **Los dos casos reales donde sí importa:**
- **Begin Step**: leer la entrada del jugador antes de que nadie la use.
- **End Step**: mover la cámara **después** de que el jugador se haya movido, para que no
  tiemble.

---

## 5. Alarmas

*«Nos permiten hacer que ocurran ciertos eventos cada tantos frames.»* Hay 12 (`alarm[0]` a
`alarm[11]`).

**Las tres reglas que da el vídeo, y las tres son correctas:**

1. **Una alarma apagada vale `-1`.**
2. **Ponerla a `0` no ejecuta nada**: se salta.
3. Si la enciendes en el **Step**, protégela con un `if`, o nunca llegará a `-1`:

```gml
// ❌ En el Step: se reinicia cada paso, la alarma nunca dispara
alarm[0] = 60;

// ✅ En el Step
if (alarm[0] == -1) alarm[0] = 60;

// ✅ O directamente en el Create, y se reactiva dentro del propio evento de alarma
```

```gml
// Create
alarm[0] = 60;

// Alarm 0  — un enemigo que dispara cada 60 frames
instance_create_layer(x, y, "Instances", obj_bala);
alarm[0] = 60;   // se rearma sola
```

> 🔺 **Ojo con los 60 frames.** Las alarmas cuentan **pasos del juego**, no segundos. Si cambias
> la velocidad del juego cambia el tiempo real. Para tiempo real usa
> **time sources** (`call_later`, `time_source_create`):
> `python3 "_indice/buscar.py" --listar time_source_`.

---

## 6. Draw

*«Puedes dibujar aquí todo lo que gustes: texto, sprites, menús, efectos especiales.»*

**Las tres advertencias del vídeo, todas importantes:**

### 6.1 · Si escribes en Draw, el sprite deja de dibujarse

```gml
// Draw
draw_self();      // ← sin esto, el personaje desaparece
draw_text(x, y - 40, nombre);
```

### 6.2 · Solo código de dibujo

> *«El resto del código hazlo en el Step o en una alarma, ya que este es uno de los eventos que
> más recursos ocupa.»*

### 6.3 · Si el objeto es invisible, el Draw NO se ejecuta

> *«Por eso también se recomienda solo código de dibujo: si por alguna razón el objeto se vuelve
> invisible, puede dejar de funcionar.»*

**Esta es la razón real** por la que la lógica no va en Draw: no es solo rendimiento, es que
`visible = false` **apaga el evento entero**.

### 6.4 · Orden de dibujado

> *«Si dibujas algo en primer lugar y después dibujas otra cosa, lo segundo va a estar por
> encima de lo primero.»*

También existen **Draw Begin** y **Draw End**.

📖 El orden completo de renderizado (room → viewport → cámara → application surface → ventana →
GUI) está en [`01 - Fundamentos/11 · Dibujo y renderizado`](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md)
y en los [cursos 41-44 de PixelatedPope](../03%20-%20Cursos%20%28YouTube%29/_INDICE-CURSOS.md).

---

## 7. Draw GUI — el HUD

*«Es muy parecido al anterior, pero todo lo que dibujes va a estar en las esquinas de la
pantalla. No importa cuántas modificaciones hagas a la cámara: esto siempre se va a dibujar por
encima de todo.»*

**Es el evento para el HUD**: barras de vida, puntuación, indicadores. También tiene sus
versiones **Begin** y **End**.

> 🔺 **Novedad de 2026 que el vídeo no puede conocer:** ya no hace falta dibujar el HUD a mano.
> Existen las **UI Layers** con **Flexpanels** (flexbox), que colocan la interfaz de forma
> adaptable sin escribir una línea de `draw_*`.
> Ver [`02 - Novedades 2026/04 · UI Layers y Flexpanels`](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md).

---

## 8. Eventos de entrada (teclado, ratón, gestos)

Los tres modos, para teclas y botones:

| Modo | Cuándo se dispara |
|---|---|
| **Pressed** | El frame en que **pulsas** |
| **Down** (el vídeo lo llama *«mantener»*) | Mientras **mantienes** |
| **Released** | El frame en que **sueltas** |

Y los de **gestos** (`Tap`, `Double Tap`, `Drag`…) para móvil.

> 💡 **La recomendación del autor es buena y conviene seguirla:** *«Yo no usaría ninguno de estos
> eventos, porque en GML tú puedes tener una función que haga eso en el código. En el Step ya
> puedes colocar cinco funciones de golpe con cinco teclas distintas, y es mucho más fácil
> cambiarlas y modificarlas.»*

```gml
// Step — todo el input en un sitio, remapeable
if (keyboard_check(vk_right)) x += 4;
if (keyboard_check(vk_left))  x -= 4;
if (keyboard_check_pressed(vk_space)) saltar();
```

> 🔺 **Y el paso siguiente:** para un juego real usa la librería **Input** de offalynne
> (teclado + ratón + mando + remapeo + multijugador local, resuelto). Está descargada en
> `11 - Código descargado/librerias/entrada/Input/` y el propio autor le dedica
> [un vídeo en español](https://youtu.be/mcJ86swsjNE).

---

## 9. Collision

*«Se ejecuta cuando colisionan las dos máscaras de colisión de los objetos.»*

Dentro del evento, **`other` es el otro objeto**:

```gml
// Collision con obj_bala, dentro de obj_enemigo
hp -= other.danio;              // danio de la bala
with (other) instance_destroy(); // destruye la bala
if (hp <= 0) instance_destroy();
```

> *«Si quieren bajarle la vida al enemigo al colisionar, pueden ocupar la palabra `other` y
> hacer `other.hp`: así van a afectar las variables de ese objeto y no las tuyas.»*

📖 La máscara de colisión se configura en el editor de sprites.
Ver [`01 - Fundamentos/08 · Movimiento y colisiones`](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md).

---

## 10. Otros eventos

*«No se usan con mucha regularidad, pero es bueno tenerlos en cuenta.»*

| Evento | Cuándo se dispara | Uso típico que da el autor |
|---|---|---|
| **Outside Room** | La instancia sale de la room | **Destruir balas** que se van de pantalla |
| **Intersect Boundary** | Toca el borde de la room | Rebotes |
| **Outside View / Intersect View** | Respecto a un viewport | Igual, pero con la cámara |
| **Game Start / Game End** | Al arrancar y al cerrar | Cargar y guardar |
| **Room Start / Room End** | Al entrar y salir de una room | Preparar la escena |
| **Animation End** | El sprite llega al último frame | Encadenar animaciones o un efecto |
| **Animation Update / Animation Event** | Animación esqueletal (Spine) | *«Como en Cult of the Lamb»* |
| **Path Ended** | Termina un path | IA que patrulla |
| **User Events (0-15)** | Los llamas tú con `event_user(n)` | **Ordenar el código** |
| **Broadcast Message** | Mensaje desde un sprite o una secuencia | Sincronizar código con una animación |

### Los eventos de usuario merecen atención

> *«Es como crear tu propio evento. Creo un evento que se llame "disparar", otro "disparar con
> escopeta", otro "disparar con láser", y los voy llamando. De esa forma lo puedes ir ordenando
> de mejor manera.»*

```gml
// Step
if (arma == ESCOPETA) event_user(1);
```

🔺 **Matiz de 2026:** hoy, para eso, suelen ser mejores las **funciones** o los **métodos**
(cap. 12-13 del [curso de GML](./06%20-%20Curso%20de%20GML%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md)),
porque se pueden reutilizar entre objetos y aceptan argumentos. Los eventos de usuario siguen
siendo útiles cuando quieres dispararlos desde fuera con `with (obj) event_user(0)`.

### Rollback y Wallpapers

El autor duda con estos (*«creo que es un error mío porque estoy usando la versión Beta»*).
**No era error:**

- 🔺 **Rollback Start / Rollback Event**: son reales. Pertenecen al sistema de **multijugador
  con rollback** de GameMaker (hasta 4-5 jugadores, con GX.games). Ver
  [`04 - Recetas por género/14 · Multijugador`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md)
  y [`12 - Utilidades/04 · Multijugador y red`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md).
- 🔺 **Wallpapers**: también reales. Son los **Live Wallpapers de Opera GX**, un target propio.

---

## 11. Eventos asíncronos

*«Se refieren a cuando recibes una señal externa del programa: cuando abres una página web, o
para recibir información externa.»*

> *«Son eventos que yo nunca he usado, siento que son un poco complicados.»*

🔺 **Y sin embargo son imprescindibles en cuanto tu juego toca el mundo exterior.** Los que de
verdad vas a usar:

| Evento asíncrono | Para qué |
|---|---|
| **HTTP** | Respuestas de `http_get` / `http_request` — tablas de clasificación, APIs |
| **Save/Load** | Guardado asíncrono en consolas y móvil |
| **Dialog** | Respuesta de `show_question_async`, `get_string_async` |
| **Networking** | Sockets TCP/UDP |
| **Steam / Social / IAP** | Respuestas de las extensiones de tienda |
| **Image Loaded** | `sprite_add` desde una URL o disco |
| **System** | Conexión y desconexión de mandos |

📖 `python3 "_indice/buscar.py" --manual "Async"` y
[`12 - Utilidades/03 · Integraciones con servicios`](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md).

---

## Resumen: el orden real de un frame

Lo que el vídeo describe pieza a pieza, junto:

```
1.  Begin Step
2.  Alarmas
3.  Step                    ← aquí va tu lógica
4.  Colisiones
5.  End Step
6.  Draw Begin
7.  Draw                    ← aquí solo dibujo
8.  Draw End
9.  Draw GUI Begin
10. Draw GUI                ← aquí el HUD
11. Draw GUI End
```

📖 El orden completo, con todos los casos borde, en
[`01 - Fundamentos/06 · Eventos y ciclo del juego`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md).
**Es el documento más importante de esta biblioteca.**

---

## Método de esta transcripción

Subtítulos originales en español descargados con `yt-dlp`, limpiados y reordenados en capítulos.
Las citas entre comillas son literales del autor; el código lo ha escrito esta biblioteca y está
verificado contra `_indice/buscar.py`. Las marcas 🔺 son anotaciones de 2026: correcciones,
avisos y lo que el motor ha añadido desde que se grabó el vídeo.
