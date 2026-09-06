# 02 · Altair_AML — GameMaker 2024 en español

> **Lo más moderno que existe en castellano sobre GML.** No es un curso cerrado, son piezas
> sueltas, pero cubren el lenguaje tal y como se escribe hoy.
> Canal: [Altair_AML](https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw) (`@ArtMakerAML`)
> Todos los datos verificados con `yt-dlp` el 1 de septiembre de 2026.

---

## Por qué merece la pena

Es el **único material en español que enseña GML con structs, métodos y el IDE moderno**.
Todo lo demás en castellano se detiene en GameMaker: Studio 1.4 o 2.x temprano.

Su vídeo estrella —*Introducción Completa al Lenguaje de programación Game Maker 2024*, 52
minutos— es, a día de hoy, **la mejor clase de GML en español que puedes ver de una sentada**.

⚠️ **Límite honesto:** el contenido es de **2023-2024**. No cubre nada de LTS 2026: ni
*handles*, ni UI Layers, ni Flexpanels, ni el sistema de partículas nuevo, ni GMRT. Para eso,
[`02 - Novedades 2026`](../02%20-%20Novedades%202026/).

⚠️ **Sin subtítulos.** Ninguno de los vídeos tiene pista de subtítulos (`yt-dlp` devuelve
`subs=NA`). Es audio en español directo.

---

## Bloque 1 · El lenguaje y el entorno (2024) ★

**Empieza por aquí si vienes de cero y quieres oírlo en español.**

| # | Vídeo | Duración | Fecha | Qué cubre |
|---|---|---:|---|---|
| 1 | [Introducción Completa al Lenguaje de programación Game Maker 2024](https://youtu.be/UneMzjBKODs) | **52:49** | 21-03-2024 | El GML actual de principio a fin: tipos, variables, control de flujo, funciones, ámbito |
| 2 | [Introducción a los EVENTOS](https://youtu.be/tPUNtpHVFSw) | 16:17 | 26-03-2024 | Create, Step, Draw, Alarm, Collision y el orden en que se ejecutan |
| 3 | [Interfaz General](https://youtu.be/KRJhX4YgcHo) | 17:08 | 02-04-2024 | Recorrido por el IDE: Asset Browser, editores, Output |

**Total: 1 h 26 min.**

### Cómo encajarlo con la biblioteca

| Después de ver… | Lee… | Para… |
|---|---|---|
| *Introducción Completa al Lenguaje* | [`01 - Fundamentos/02 · Tipos y variables`](../01%20-%20Fundamentos/02%20-%20Tipos%20de%20datos%20y%20variables.md) y [`07 · Funciones, métodos y ámbito`](../01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md) | Fijar lo visto y añadir lo que cambió en 2026 |
| *Introducción a los EVENTOS* | [`01 - Fundamentos/06 · Eventos y ciclo del juego`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) | El orden completo de eventos y `delta_time` |
| *Interfaz General* | [`01 - Fundamentos/01 · El IDE y el flujo de trabajo`](../01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) | Las novedades del IDE 2026: Code Editor 2, Feather, Package Manager |

---

## Bloque 2 · Conceptos y herramientas (2023)

| # | Vídeo | Duración | Fecha | Qué cubre |
|---|---|---:|---|---|
| 4 | [¿Qué son los Structs?](https://youtu.be/gzRbXITRS9Q) | 3:49 | 31-01-2023 | Introducción rápida a los structs de GML |
| 5 | [Mejora tu proyecto con INPUT](https://youtu.be/mcJ86swsjNE) | 11:00 | 29-01-2023 | Cómo integrar la librería **Input** de offalynne |
| 6 | [Cómo crear diálogos fácilmente con Scribble](https://youtu.be/rxsPzpbBv74) | 7:23 | 28-01-2023 | Cómo integrar **Scribble** de Juju Adams para texto y diálogos |

> 💎 Los vídeos 5 y 6 son especialmente valiosos: son **las únicas explicaciones en español**
> de las dos librerías más importantes del ecosistema. Y las tienes descargadas:
> `11 - Código descargado/librerias/entrada/Input/` y
> `11 - Código descargado/librerias/texto-y-tipografia/Scribble/`.
>
> Amplía con [`07 - Ecosistema/02 · Librerías esenciales`](../07%20-%20Ecosistema/02%20-%20Librer%C3%ADas%20esenciales%20de%20la%20comunidad.md).

Para los structs, el vídeo 4 se queda muy corto (3:49). Complétalo con
[`01 - Fundamentos/04 · Structs y constructores (POO en GML)`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md),
que cubre `constructor`, `new`, herencia con `:` y `static`.

---

## Bloque 3 · Tutorial de Mega Man X (2022-2023) — 6 partes

Un plataformas de acción construido paso a paso. **Es el tutorial de plataformas más completo
en español posterior a GMS 1.4.**

| Parte | Vídeo | Duración | Fecha | Sistema que construye |
|---|---|---:|---|---|
| 1 | [Físicas básicas](https://youtu.be/2LRKvF5C6iw) | 19:09 | 11-12-2022 | Gravedad, movimiento horizontal, colisión con suelo |
| 2 | [Wall jump, escalera y deslizamiento](https://youtu.be/uiUe-szy53Q) | 14:16 | 18-12-2022 | Salto de pared, escaleras, *slide* |
| 3 | [Cambio de sprites + sonido](https://youtu.be/4-NfzClhBJQ) | 10:14 | 30-12-2022 | Máquina de animaciones y audio |
| 4 | [X-Buster](https://youtu.be/zNOLaiAyXgg) | 9:40 | 08-01-2023 | Disparo con carga |
| 5 | [Dash](https://youtu.be/AcImiGbQaow) | 7:20 | 14-01-2023 | Impulso horizontal con estado propio |
| 6 | [Damage e intro](https://youtu.be/e1jeJAU0cQY) | 11:54 | 25-01-2023 | Daño, retroceso y secuencia de entrada |

**Total: 1 h 12 min.** Playlist del canal:
<https://www.youtube.com/playlist?list=PLVuK8v4p-jeQTjoC337Vdymf0xVJZi8zm>

### Cómo aprovecharlo

Sigue el tutorial y en paralelo lee
[`04 - Recetas por género/01 · Plataformas 2D`](../04%20-%20Recetas%20por%20g%C3%A9nero/01%20-%20Plataformas%202D.md).
La receta te dice qué le falta al tutorial para que el juego «se sienta bien»: **coyote time**,
**jump buffering**, altura de salto variable y *squash & stretch*
([`04 - Recetas/15 · Game feel y juice`](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md)).

Para comparar con implementaciones reales de un plataformas de acción, tienes el código de
`OrbinautFramework` y `MegamixEngine` en
[`11 - Código descargado/juegos_y_motores/`](../11%20-%20C%C3%B3digo%20descargado/juegos_y_motores/).

---

## Otros vídeos del canal

| Vídeo | Duración | Notas |
|---|---:|---|
| [Approach, un script indispensable](https://youtu.be/niwwb1zd3vg) | 2:00 | La función `approach`, patrón clásico para interpolar valores. Está implementada en `06 - Assets y Scripts/scr_math_util.gml` |
| [Simple Mechanic — Color Changing](https://youtu.be/NftT3-OQpOU) | 3:00 | Cambio de paleta por código |
| [MegaMan engine v0.7 (final)](https://youtu.be/qIe2FpsBGgU) | 1:00 | Demostración del motor terminado |

> El canal tiene además una serie sobre **Pixel Game Maker MV**, que es **otro motor
> distinto** (de Kadokawa, no de YoYo Games). No la mezcles.

---

## Veredicto

| Aspecto | Valoración |
|---|---|
| Actualidad | 🟡 2024 — lo más nuevo en español, pero no llega a LTS 2026 |
| Profundidad del lenguaje | 🟢 Alta: 52 minutos seguidos de GML explicado |
| Estructura de curso | 🟠 Piezas sueltas, no hay progresión cerrada |
| Producción | 🟢 Clara y directa |
| Subtítulos | 🔴 Ninguno |
| Cobertura de 2026 | 🔴 Nula |

**Úsalo así:** los tres vídeos de 2024 como *clase magistral* de GML en español, el tutorial
de Mega Man X como práctica guiada, y esta biblioteca para todo lo posterior a 2024.

## Fuentes

- Canal: <https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw>
- Playlist Mega Man X: <https://www.youtube.com/playlist?list=PLVuK8v4p-jeQTjoC337Vdymf0xVJZi8zm>
- Playlist Game Maker Studio 2: <https://www.youtube.com/playlist?list=PLVuK8v4p-jeSoVU6ytO6IRZ_xoMJfnnpz>
