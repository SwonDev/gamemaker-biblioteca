# 36 · DragoniteSpam — ¿Por qué todo se ve borroso?

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 24 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=i1DAeEFp9Xs> |
| **Duración** | 8 min 4 s |
| **Publicado** | 25 de julio de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `gpu_set_texfilter()` |

> «La pregunta de **por qué a veces los sprites se ven todos borrosos** al ejecutar el
> juego, aunque no lo estén en el editor de sprites ni en el editor de rooms, es
> probablemente **la pregunta más común** que veo de nuevos usuarios de GameMaker en los
> últimos dos años.»

Capítulo corto, directo y con tres soluciones.

## Índice de contenido

1. Solución 1: la casilla en los ajustes
2. Solución 2: por código con `gpu_set_texfilter()`
3. Solución 3: la plantilla al crear el proyecto
4. Qué es el filtrado de texturas, técnicamente
5. Cuándo aparece el problema
6. Por qué conviene una cámara más pequeña
7. Una queja justificada a GameMaker

---

## 1. Solución 1: la casilla en los ajustes

Es la más fácil y la que querrá la mayoría.

```
Game Options → [tu plataforma: Windows / macOS / Ubuntu] → Graphics → ☐ Interpolate colors between pixels
```

1. Desmarca **«Interpolate colors between pixels»**.
2. Pulsa **OK** y aplica.

Al ejecutar, los píxeles dejan de estar borrosos y se usa **escalado «nearest neighbor»**
(vecino más cercano), que mantiene el pixel art **nítido**.

---

## 2. Solución 2: por código con `gpu_set_texfilter()`

También puedes cambiar el ajuste **en tiempo de ejecución**:

```gml
gpu_set_texfilter(false);   // Desactivar interpolación = pixel art nítido
```

Es el **equivalente directo en código** a la casilla de los ajustes.

```gml
// Step event, por ejemplo
if (keyboard_check(vk_enter))
{
    gpu_set_texfilter(false);   // Nítido
}

if (keyboard_check(vk_space))
{
    gpu_set_texfilter(true);    // Borroso
}
```

### ¿Para qué querrías cambiarlo en marcha?

El autor da el caso más útil:

> En un juego de pixel art con **interfaz en alta definición** puede interesar tener el
> filtrado **desactivado** al dibujar el juego (sprites, fondos, tiles) y **activado** al
> dibujar los elementos de interfaz.

---

## 3. Solución 3: la plantilla al crear el proyecto

Al crear un proyecto nuevo hay dos plantillas de juego en blanco:

| Plantilla | Ajuste por defecto |
|---|---|
| **Blank game** | Interpolación **ACTIVADA** |
| **Blank pixel game** | Interpolación **DESACTIVADA** |

> **Esa es literalmente la única diferencia entre las dos plantillas.**

El autor calcula que **alrededor del 80 %** de la gente que crea un proyecto en GameMaker
querrá la de pixel.

(Nota: al cambiar entre plantillas también aparece el selector de **GML Code** frente a
**GML Visual**, así que puede haber algún otro ajuste menor.)

---

## 4. Qué es el filtrado de texturas, técnicamente

> El **filtrado de texturas** afecta a cómo se muestran los sprites y a cómo se **muestrean
> las texturas** (en términos de shader) **cuando no estás dibujando un sprite en una
> relación exacta 1:1 con la rejilla de píxeles** a la que dibujas.

Traducción: si hay algún desajuste entre el tamaño de tu vista y el de la ventana,
GameMaker tiene que «adivinar» los píxeles intermedios, y eso es lo que produce el
difuminado.

---

## 5. Cuándo aparece el problema

En el proyecto de ejemplo, la cámara es de **360 × 180** pero se amplía a una ventana de
**1366 × 768**.

### Caso A: relación 1:1

Si ajustas la cámara para que su tamaño sea **exactamente** el de la ventana:

> **No verás ningún artefacto.** Los sprites se dibujan 1:1 y se ven perfectos.

### Caso B: en cuanto introduces escalado

> En el instante en que introduces **cualquier escalado** —ya sea ampliando con las
> funciones de cámara de GameMaker o con los ajustes de viewport del editor de rooms—
> aparecen los artefactos de interpolación en los bordes de los sprites.

Y esto ocurre **incluso si la ampliación es exactamente 2:1**.

### Caso C: en cuanto introduces rotación

> Si dibujas un sprite **rotado** (por ejemplo 60°) en lugar de sin rotar, también empiezan
> a aparecer artefactos.

---

## 6. Por qué conviene una cámara más pequeña

> La regla general al hacer juegos de pixel art es **crear una cámara más pequeña que el
> tamaño real de la ventana**, para no tener que lidiar con subpíxeles de formas raras y
> molestas.

Pero claro, eso significa que vas a escalar… y por eso:

> Si tienes la interpolación de texturas **activada**, es **extremadamente común** toparse
> con este problema. En el momento en que haces zoom de viewport, escalado o rotación,
> va a pasar.

---

## 7. Una queja justificada a GameMaker

El autor cierra dirigiéndose directamente a GameMaker:

> «Sé que a veces veis estos vídeos, y **tenemos que mejorar en esto**. Como mínimo,
> **el icono de la plantilla *blank pixel game* no ayuda en absoluto**. Y ojalá este no
> fuera un vídeo que tuviera que hacer.»

Y explica por qué lo hace igualmente:

> «Es, con mucha diferencia, el problema más común que veo aparecer en el subreddit de
> GameMaker, en el Discord, en los foros y prácticamente en todos los demás entornos
> sociales de GameMaker en internet. Sería estupendo que esto dejara de ser un problema que
> la comunidad tiene que responder constantemente **por culpa de un único ajuste mal
> comunicado en la página de inicio de GameMaker**.»

---

## Puntos clave

1. **Es el problema más común** de los nuevos usuarios de GameMaker.
2. **Solución 1:** desmarca **Interpolate colors between pixels** en
   **Game Options → [plataforma] → Graphics**.
3. **Solución 2:** **`gpu_set_texfilter(false)`** por código, en cualquier momento.
4. **Solución 3:** crea el proyecto con la plantilla **Blank pixel game**.
5. **La única diferencia entre las dos plantillas es ese ajuste.**
6. El filtrado suaviza cuando **no hay relación 1:1** con la rejilla de píxeles.
7. Aparece al **escalar** (aunque sea 2:1 exacto) y al **rotar**.
8. Puedes alternarlo en marcha: desactivado para el juego, activado para la interfaz en HD.
9. En pixel art conviene **una cámara más pequeña que la ventana**, lo que hace este ajuste
   aún más importante.
10. La comunidad lo sufre por un ajuste mal comunicado en la pantalla de inicio.

---

## Ejercicio propuesto

> **Objetivo:** reproducir el problema, entender exactamente cuándo aparece y dominar las
> tres soluciones.

**Parte A — Reproducirlo**

1. Crea un proyecto con la plantilla **Blank game** (interpolación activada).
2. Crea un sprite de pixel art pequeño y nítido (por ejemplo 16 × 16 con líneas duras).
3. Ejecuta **sin zoom de cámara**: comprueba que se ve bien.
4. Configura una cámara más pequeña que la ventana (por ejemplo 360 × 180 ampliada a
   1366 × 768) y ejecuta. **Observa el difuminado.**
5. Ahora pon la cámara al **tamaño exacto de la ventana** y comprueba que vuelve a verse
   nítido, aunque el ajuste siga activado.

**Parte B — Las tres soluciones**

6. Ve a **Game Options → [tu plataforma] → Graphics** y desmarca la casilla. Comprueba la
   mejora.
7. Vuélvela a **activar** y en su lugar pon `gpu_set_texfilter(false);` en el **Create** de
   tu objeto. Comprueba que funciona igual.
8. Crea un proyecto nuevo con **Blank pixel game** y verifica que por defecto ya está
   desactivado.

**Parte C — Alternarlo en marcha (el caso útil)**

9. Con la interpolación activada por ajustes, añade esto al Step:
   ```gml
   if (keyboard_check(vk_enter)) { gpu_set_texfilter(false); }
   if (keyboard_check(vk_space)) { gpu_set_texfilter(true);  }
   ```
10. Juega con ambas teclas y observa la diferencia en vivo.

**Parte D — Rotación**

11. Dibuja tu sprite **rotado 60°** con `draw_sprite_ext()` y comprueba que la rotación
    **también** produce artefactos con el filtrado activado.

**Reto extra:** monta el caso que propone el autor: un juego de pixel art con **interfaz en
alta definición**. Desactiva el filtrado al dibujar el juego y actívalo solo dentro del
evento **Draw GUI**, y compáralo con tenerlo siempre activado o siempre desactivado. Anota
cuál se ve mejor y por qué.
