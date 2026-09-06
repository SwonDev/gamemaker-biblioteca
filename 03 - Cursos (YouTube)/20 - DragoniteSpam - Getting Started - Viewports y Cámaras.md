# 20 · DragoniteSpam — Viewports y cámaras

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 8 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=wK67S3qKo-U> |
| **Duración** | 15 min 5 s |
| **Publicado** | 31 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno (configuración desde el editor) |

El problema que arrastra el autor desde hace varios vídeos: al ejecutar, el juego muestra
**la room entera** y el personaje es diminuto. Hay que entrecerrar los ojos para ver qué
hace.

## Índice de contenido

1. Una advertencia honesta sobre las cámaras
2. Dónde están los ajustes
3. Habilitar viewports
4. Propiedades de la cámara
5. Posición X e Y de la cámara
6. Seguimiento de un objeto
7. Bordes horizontal y vertical: centrar al jugador
8. Velocidades horizontal y vertical: inercia
9. Propiedades del viewport: la región de la ventana
10. Varios viewports: pantalla dividida
11. Cuándo dejar de usar el sistema integrado

---

## 1. Una advertencia honesta sobre las cámaras

> «Encontrarás gente discutiendo a gritos en internet sobre por qué su forma de manejar
> views y cámaras es la mejor. **En su mayor parte, eso es una tontería.**»

Distintos juegos necesitan cosas distintas de su cámara:

- Un **RPG cenital** tipo Dragon Quest o *Link to the Past*.
- Un **juego de plataformas lateral** tipo Super Mario.

Tienen necesidades completamente diferentes. El autor no entra en filosofía de diseño,
sino en **cómo se configura técnicamente**.

### Su valoración del sistema integrado

> «No creo que el sistema de viewports y cámaras de GameMaker sea tan malo como parece
> pensar la mayoría, **al menos no para juegos pequeños**. Si haces un juego pequeño y
> necesitas algo que funcione, **es perfectamente válido**».

Pero si quieres transiciones dinámicas entre personajes y comportamientos elaborados,
**escribe tu propio sistema**.

---

## 2. Dónde están los ajustes

En el editor de rooms, en el **inspector de la room**, hay una pestaña **Viewports and
Cameras**.

> Si has hecho clic en otra cosa (una capa, un objeto) y ha cambiado el panel, recuperas
> el inspector de la room **cerrando y reabriendo la room**, o **haciendo clic en la
> pestaña superior** con el nombre de la room (por ejemplo `rm_level1`).

---

## 3. Habilitar viewports

Por defecto el sistema está **desactivado** y GameMaker muestra la room entera en la
ventana.

Para activarlo:

1. Marca **Enable Viewports**.
2. Marca **Visible** en **Viewport 0**.

> GameMaker permite hasta **ocho viewports**, indexados **del 0 al 7** (chiste del autor
> sobre los «dos problemas difíciles» de la informática, más los errores *off-by-one*).

Al marcar *Visible*, aparece un **rectángulo blanco** en la room: es la **parte de la room
que la cámara ve**.

---

## 4. Propiedades de la cámara

La room por defecto mide **1366 × 768**. El autor quiere una vista de **640 × 360**
centrada en el jugador.

| Propiedad | Valor de ejemplo |
|---|---|
| **Width** | 640 |
| **Height** | 360 |

Al ejecutar, esa esquina de la room se **amplía para rellenar toda la ventana**.

> Pero **no sigue al jugador**: si te sales de la vista, desapareces.

---

## 5. Posición X e Y de la cámara

Puedes mover el rectángulo a mano (por ejemplo a 400, 200) para enfocar otra zona.

> El autor opina que fijar la posición en el editor **no suele ser muy útil**: lo normal
> es querer que la vista **siga al jugador**, no que ocupe una coordenada fija.

Aun así, la opción existe para los casos en que sí quieras una vista fija.

---

## 6. Seguimiento de un objeto

En **View Following → Object Following**, donde pone *no object*, elige `obj_player`.

Ahora la cámara se mueve cuando te acercas a los bordes.

> **No te sigue fuera de la room**: si llegas al límite, sales de la vista y la cámara se
> queda. En GameMaker puede existir contenido fuera de las rooms, pero el sistema de
> views por defecto **nunca sale de la room**.

---

## 7. Bordes horizontal y vertical: centrar al jugador

El comportamiento por defecto resulta extraño: tienes que llegar **casi al borde** de la
vista para que esta se mueva.

> «Da la sensación de que **estamos empujando la vista con el casco**, más que de que la
> cámara nos siga.»

Los **bordes horizontal y vertical** definen **a qué distancia del lado de la vista** tiene
que llegar el jugador para que la vista empiece a moverse.

| Ajuste | Efecto |
|---|---|
| Bordes pequeños | La vista se mueve solo al llegar muy al borde |
| **Horizontal = mitad del ancho de la vista** | El jugador queda **centrado horizontalmente** |
| **Vertical = mitad del alto de la vista** | El jugador queda **centrado verticalmente** |

Con una vista de 640 × 360:

```
Horizontal Border = 320   (la mitad de 640)
Vertical Border   = 180   (la mitad de 360)
```

> En la práctica, el «borde» pasa a ser media pantalla: el jugador está siempre centrado y
> la cámara salta a su posición.

Las excepciones son los **límites de la room**: ahí la cámara se detiene.

---

## 8. Velocidades horizontal y vertical: inercia

Por defecto, la cámara **salta** instantáneamente a la posición del jugador.

Las propiedades **Horizontal Speed** y **Vertical Speed** permiten darle **inercia**:

| Valor | Efecto |
|---|---|
| **−1** (negativo) | Velocidad infinita: la cámara **salta** a la posición |
| **3**, por ejemplo | La cámara **va por detrás** y tarda un momento en alcanzarte |

El jugador se mueve a 4 píxeles por paso, así que con velocidad 3 la cámara se retrasa
visiblemente y **tarda en recuperarse al parar**.

> El autor **no** quiere esto para este juego: «la mayoría de las veces, que la cámara se
> retrase al moverte resulta un poco desorientador».

Dónde **sí** tiene sentido:

- Si el jugador **se teletransporta** y quieres que la cámara haga un scroll.
- Si cambias el objeto seguido y quieres que la cámara se desplace hasta él.

---

## 9. Propiedades del viewport: la región de la ventana

> **Diferencia clave:**
>
> - **Camera properties** = los límites **dentro del mundo del juego** sobre los que se
>   enfoca la cámara.
> - **Viewport properties** = la región **de la ventana/pantalla** donde se dibuja eso,
>   **fuera del mundo del juego**.

Por defecto el viewport tiene el alto y ancho de la ventana del juego (que a su vez tiene
el de la room).

Si pones el viewport a 640 × 360:

> Verás el mismo rectángulo siguiendo al jugador, pero **la ventana será mucho más
> pequeña**. Y **no estará ampliada**: son 640 × 360 reales.

### Posición X e Y del viewport

Solo importa realmente si tienes **varios viewports**. Desplazar el viewport a (100, 100)
hace que el rectángulo de la cámara **no nazca en la esquina** de la ventana, sino
desplazado.

---

## 10. Varios viewports: pantalla dividida

Con dos viewports podrías tener:

- Uno ocupando la **mitad izquierda** de la pantalla.
- Otro ocupando la **mitad derecha**.

Útil para **multijugador en pantalla dividida**.

> El autor no entra en detalle: «se complica y se ensucia bastante rápido». Y recomienda
> **hacerlo por código** en lugar de con el sistema integrado.

---

## 11. Cuándo dejar de usar el sistema integrado

> Si quieres más, tendrás que mirar el **código**: hay bastantes funciones relacionadas con
> views y cámaras accesibles mediante GML.

Recomendación del autor para profundizar: **la serie de vídeos sobre views y cámaras de
Pixelated Pope**, mucho más detallada.

---

## Puntos clave

1. **Enable Viewports** + **Visible** en el viewport 0 activa el sistema.
2. El **rectángulo blanco** muestra qué parte de la room ve la cámara.
3. **Hasta 8 viewports**, indexados **0-7**.
4. **Object Following** hace que la cámara siga a un objeto.
5. **La cámara nunca sale de los límites de la room.**
6. **Bordes = la mitad del tamaño de la vista** → el jugador queda **centrado**.
7. **Velocidades −1** = salto instantáneo; un valor positivo da **inercia**.
8. **Camera properties** = límites en el mundo; **Viewport properties** = región de la
   pantalla.
9. Varios viewports permiten **pantalla dividida**, mejor por código.
10. Para juegos pequeños el sistema integrado **es perfectamente válido**; para cámaras
    elaboradas, escribe el tuyo.

---

## Ejercicio propuesto

> **Objetivo:** configurar una cámara que siga al jugador y entender la diferencia entre
> cámara y viewport.

1. Abre la room y ve a la pestaña **Viewports and Cameras**. Si no aparece, haz clic en la
   pestaña superior con el nombre de la room.
2. Marca **Enable Viewports** y **Visible** en el viewport 0. Observa el rectángulo blanco.
3. Pon el ancho y alto de la cámara a **640 × 360**. Ejecuta y comprueba que se amplía para
   rellenar la ventana… pero que **no te sigue**.
4. Fija a mano **X = 400** e **Y = 200** y comprueba cómo enfoca otra zona. Después
   vuelve a dejarlo en 0, 0.
5. Asigna **Object Following → obj_player**. Comprueba que ahora sí te sigue.
6. **Salte al límite de la room** y verifica que la cámara **no sale** de ella.

**Parte de ajuste fino**

7. Deja los bordes en su valor por defecto y fíjate en lo cerca que tienes que llegar al
   borde. Describe la sensación de «empujar la ventana con el casco».
8. Pon **Horizontal Border = 320** y ejecuta. Comprueba que ahora estás centrado
   horizontalmente pero **no** verticalmente.
9. Añade **Vertical Border = 180** y comprueba el centrado completo.

**Parte de inercia**

10. Pon **Horizontal Speed = 3** y observa el retraso de la cámara. ¿Te resulta agradable o
    desorientador?
11. Vuelve a poner **−1** para el salto instantáneo.

**Reto extra:** cambia las **Viewport properties** a 640 × 360 **sin** tocar la cámara, y
comprueba que la ventana se encoge **sin ampliar nada**. Explica con tus palabras la
diferencia entre el tamaño de la cámara y el tamaño del viewport, y por qué confundirlos
es el error más común al empezar con cámaras en GameMaker.
