# Blogs, newsletters y fuentes de información continua

> Verificado a 31 de agosto de 2026.
> **Prioridad**: release notes > blog oficial > manual > blogs de la comunidad.

---

## 1. Fuentes oficiales — lo único que *tienes* que seguir

### 1.1 Release notes ★ la fuente de verdad

**<https://releases.gamemaker.io/>**

- Aquí se publica cada cambio de cada versión, incluidas las betas y GMRT.
- **LTS 2026.0.0 (IDE 16 / Runtime 23)**: <https://releases.gamemaker.io/release-notes/2026/0>
- GMRT: <https://releases.gamemaker.io/release-notes/2026/GMRT_MS_20.html>
- La propia web lo dice: *«LTS2026 is the version that we recommend everyone should use
  nowadays»*.

**Por qué es la fuente de verdad y no el blog**: el blog anuncia, las release notes
**documentan**. Cuando algo deja de funcionar tras actualizar, la respuesta está aquí, no
en ningún vídeo.

**Suscríbete**: la web ofrece RSS en el pie (`RSS for Node`). Añádelo a tu lector de feeds.

### 1.2 Blog oficial

**<https://gamemaker.io/en/blog/>** · **Feed RSS: <https://gamemaker.io/blog/rss>** ★

Contenido típico: entrevistas a estudios que usan GameMaker, *post-mortems*, tutoriales
puntuales, anuncios de extensiones y convocatorias de jams.

Posts verificados de 2026 (del feed RSS):

| Fecha | Post | Enlace |
|---|---|---|
| 19 ago 2026 | Loop Hero (Playdigious) — port de PC a móvil de un juego de éxito conocido | <https://gamemaker.io/en/blog/pc-to-mobile-loop-hero> |
| 22 jul 2026 | Making A Rhythm Game In GameMaker | <https://gamemaker.io/blog/make-rhythm-game> |
| 15 jul 2026 | Why We Stuck With GameMaker — Space Scum | <https://gamemaker.io/blog/space-scum-why> |
| 13 jul 2026 | **Photon GameMaker Extension Release** (multijugador) | <https://gamemaker.io/blog/photon-extention-release> |
| 8 jul 2026 | The King Is Watching: From Game Jam to 600k Sales | <https://gamemaker.io/blog/the-king-is-watching-tinybuild> |
| 5 ago 2026 | **Bringing Real-Time Multiplayer to GameMaker with Colyseus** (beta) | <https://gamemaker.io/en/blog/colyseus-multiplayer> |
| 1 jul 2026 | Cause+Select — proyecto benéfico | <https://gamemaker.io/en/blog/cause-select-charity> |
| 24 jun 2026 | Chivalware (respaldado por The Arcade Crew) | <https://gamemaker.io/en/blog/arcade-crew-chivalware> |
| 4 jun 2026 | Discord Social SDK Extension Update | <https://gamemaker.io/blog/discord-social-sdk> |
| 20 may 2026 | **GameMaker LTS 2026.0: New Features, GMRT and Much More** | <https://gamemaker.io/en/blog/lts-2026-release> |
| 13 may 2026 | Barty's Adventure — entrevista al estudio | <https://gamemaker.io/en/blog/bartys-adventure-interview> |
| 29 abr 2026 | **GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future** | <https://gamemaker.io/en/blog/update-spring-2026> |
| 20 ene 2026 | Micro Jam: A Bi-Weekly Game Jam Community | <https://gamemaker.io/blog/micro-jam> |
| 16 ene 2026 | Namazu Elements (multijugador) | <https://gamemaker.io/blog/namazu-elements-multiplayer> |

> Cuatro filas añadidas el 2026-09-07 (verificadas con WebFetch, HTTP 200): el feed RSS oficial
> no las listaba todas — la tabla de arriba es la lista real del blog, no solo del RSS.

Los dos imprescindibles: **LTS 2026.0** y **Update Spring 2026**. El segundo contiene el
roadmap: Code Editor 2 como plugin, nueva Start Page, ProjectTool y el futuro **Prefab
Builder**.

### 1.3 Manual

**<https://manual.gamemaker.io/>** · versión LTS: <https://manual.gamemaker.io/lts/en/>

- Referencia completa de GML y del IDE. Mejor de lo que la mayoría recuerda.
- ⚠️ Aviso verificado: en LTS 2026.0.0 se reportó que el **manual offline integrado estaba
  desactualizado** respecto a las features de la versión (bug #15044). Usa la **web**, no el
  manual offline, hasta que lo corrijan.

### 1.4 Roadmap público

**<https://github.com/orgs/YoYoGames/projects/17/views/48>**

Tablero de GitHub Projects con lo planeado. Es la forma de saber si tu feature request
existe ya.

### 1.5 Rastreador de bugs

**<https://github.com/YoYoGames/GameMaker-Bugs>** ★

No es solo para reportar: es una **fuente de conocimiento técnico de primer nivel**. Las
discusiones incluyen explicaciones del equipo sobre por qué algo funciona como funciona.
Ejemplos muy instructivos:

- Issue #11835 — diferencias de `is_*()`/`typeof()` entre GMRT y GMS2 (con tabla comparativa)
- Issue #15151 — por qué `variable_clone()` no clona secuencias ni curvas de animación

### 1.6 GMCLAN — rastreador de versiones de la comunidad

**<https://gms-updates.gmclan.org/>** (por gnysek, moderador del foro)

- Página mínima que muestra la última versión de cada canal: LTS 2026, LTS 2022, betas.
- Verificado: refleja **IDE 2026.0.0.16 / Runtime 2026.0.0.23** correctamente.
- Más rápido de consultar que las release notes cuando solo quieres saber si hay versión nueva.

---

## 2. Blogs de desarrolladores — donde está el conocimiento real

### 2.1 YellowAfterlife ★ el más activo y el más profundo

| Canal | Enlace |
|---|---|
| **Newsletter (Substack)** ★ | <https://yellowafterlife.substack.com/> |
| Blog (Blogspot) | <http://yellowafterlife.blogspot.com/> |
| itch.io | <https://yellowafterlife.itch.io/> |

- Publica constantemente sobre GameMaker: *deep dives* de GML, herramientas, análisis de
  motores, retrospectivas.
- **Mantiene herramientas esenciales**:
  - **GMLive.gml** — recarga en vivo de código y assets. Actualizado en jul 2026 con soporte
    específico para LTS2026: <https://yellowafterlife.itch.io/gamemaker-live>
  - **window_shape** — ventanas con formas: <https://yellowafterlife.itch.io/gamemaker-window-shape>
- También escribe sobre localización en GameMaker (publicó su sistema como librería abierta).
- **Recomendación: suscríbete al Substack. Es lo mejor que puedes hacer por tu GML este año.**

### 2.2 Juju Adams

| Canal | Enlace |
|---|---|
| Web personal | <https://www.jujuadams.com/> |
| GitHub | <https://github.com/jujuadams> (192 repos, 648 seguidores) |
| itch.io | <https://jujuadams.itch.io/> |

- Programador de juegos en Londres. Ha trabajado en **Deltarune**, *Shovel Knight: Pocket
  Dungeon*, *Disc Room* e *Hyper Light Drifter*.
- Escribe blogs invitados para YoYo Games y da clases en universidades del Reino Unido.
- **Librerías open source imprescindibles**:
  - **Chatterbox** — lenguaje de narrativa/diálogo (175★): <https://github.com/JujuAdams/Chatterbox>
  - **Bulb** — luces y sombras 2D (107★): <https://github.com/JujuAdams/Bulb>
  - **Coroutines** (84★) · **Kawase** — blur (71★) · **Bento** — framework de UI (53★)
- ⭐ **GameMakerLibraries** — un listado curado de librerías, extensiones y herramientas de
  GameMaker: <https://github.com/JujuAdams/GameMakerLibraries>
  **Es el mejor punto de partida para no reinventar la rueda. Guárdalo.**

### 2.3 DragoniteSpam

| Canal | Enlace |
|---|---|
| itch.io | <https://dragonite.itch.io/> |

- Conocido sobre todo por sus **tutoriales de 3D en GameMaker** (YouTube) — la referencia
  absoluta si quieres hacer 3D en un motor 2D.
- Mantiene **3D Collisions in GameMaker**, con actualizaciones de rendimiento verificadas en
  feb 2026 (broadphase basada en instancias de GameMaker, hasta 10× más rápido que octree):
  <https://dragonite.itch.io/collisions>

### 2.4 Gurpreet S. Matharoo

- **Lead Technical Writer de GameMaker**. Escribe gran parte de la documentación y de los
  tutoriales oficiales, incluido el post de LTS 2026.0.
- No tiene blog personal público, pero **firma la mayoría de tutoriales oficiales**:
  seguir su autoría en <https://gamemaker.io/en/blog/> y
  <https://gamemaker.io/en/tutorials> equivale a seguirle.

### 2.5 gm(48) Developer Blogs

**<https://gm48.net/developer-blogs/>**

Agregador de blogs y *post-mortems* escritos por participantes de las jams. Contenido de
primera mano sobre cómo se construye un juego en 48 horas. Muy infravalorado.

---

## 3. GameDev.net

**<https://www.gamedev.net/>**

- ⚠️ **Bloquea clientes automáticos (HTTP 403)**, pero carga sin problema en el navegador.
- Tiene sección de GameMaker y cobertura de noticias de jams con bastante antelación.
- Fue de donde salió la noticia del **cierre anunciado de Ludum Dare en octubre de 2028**.
- Veredicto: útil como agregador de noticias de jams, secundario para GML.

---

## 4. YouTube

| Canal | Enlace | Contenido |
|---|---|---|
| **GameMaker (oficial)** | <https://www.youtube.com/@GameMakerEngine> | Tutoriales, *update videos*, directos, showcase |

El canal oficial es el punto de partida. ⚠️ **Muchísimos canales de terceros tienen
contenido de GMS 1.4 o GMS 2.2 que ya no aplica** a LTS 2026 (cambiaron los tilesets, las
secuencias, las UI layers, el sistema de partículas y el *pipeline* de proyectos). Comprueba
la fecha antes de seguir un tutorial.

Para canales específicos por temática, revisa la carpeta
`03 - Cursos (YouTube)` de este mismo repositorio.

---

## 5. Newsletters

| Newsletter | Enlace | Contenido |
|---|---|---|
| **YellowAfterlife's Newsletter** ★ | <https://yellowafterlife.substack.com/> | La única newsletter centrada en GameMaker verdaderamente activa en 2026. Posts, tutoriales, lanzamientos y comentario del ecosistema. |
| Blog oficial (RSS) | <https://gamemaker.io/blog/rss> | Anuncios y artículos del equipo |
| Release notes (RSS) | <https://releases.gamemaker.io/> (RSS en el pie) | Cada cambio de versión |

---

## 6. Podcasts — veredicto honesto

⚠️ **No existe un podcast dedicado a GameMaker activo en 2026.** Lo he buscado y no he
encontrado ninguno con episodios recientes.

Lo que **sí** encontrarás al buscar «GameMaker podcast» y que **no** es lo que buscas:

- **GameMakers** (<https://podcasts.apple.com/td/podcast/gamemakers/id1541808441>) — podcast
  de Joseph Kim sobre **negocio de juegos F2P, monetización y liveops**. Se llama
  «GameMakers» pero **no trata sobre GameMaker**. 179 episodios. Es excelente si te interesa
  el lado empresarial, irrelevante si quieres aprender GML.

Si quieres audio sobre GameMaker, las alternativas reales son:

1. El **canal de YouTube oficial** (<https://www.youtube.com/@GameMakerEngine>), que publica
   los *update videos* y directos con Q&A.
2. Los **vídeos de las GameMaker Update** anunciados en el blog, con su correspondiente hilo
   de Q&A en el foro (p. ej.
   <https://forum.gamemaker.io/index.php?threads/gamemaker-update-spring-2026-q-a.123308/>).

---

## 7. Configuración recomendada ( mínima y suficiente )

Si solo vas a seguir cinco cosas, que sean estas:

1. **RSS de release notes** — <https://releases.gamemaker.io/> → imprescindible para no
   romper tu proyecto al actualizar.
2. **RSS del blog oficial** — <https://gamemaker.io/blog/rss> → novedades y contexto.
3. **Substack de YellowAfterlife** — <https://yellowafterlife.substack.com/> → profundidad
   técnica real.
4. **Hilo de Q&A de la última GameMaker Update** en el foro → roadmap y decisiones del equipo.
5. **Discord oficial** — <https://discord.gg/gamemaker> → lo urgente del día a día.

Añade como consulta puntual: **GameMakerLibraries de Juju Adams**
(<https://github.com/JujuAdams/GameMakerLibraries>) cada vez que vayas a empezar un sistema
nuevo.

---

## 8. Tabla de verificación

| Recurso | Enlace | Estado |
|---|---|---|
| Release notes | <https://releases.gamemaker.io/> | ✅ |
| Release notes LTS 2026.0 | <https://releases.gamemaker.io/release-notes/2026/0> | ✅ |
| Release notes GMRT 0.20 | <https://releases.gamemaker.io/release-notes/2026/GMRT_MS_20.html> | ✅ |
| Blog oficial | <https://gamemaker.io/en/blog> | ✅ |
| **RSS del blog** | <https://gamemaker.io/blog/rss> | ✅ |
| Manual | <https://manual.gamemaker.io/> | ✅ |
| Roadmap | <https://github.com/orgs/YoYoGames/projects/17/views/48> | ✅ |
| GameMaker-Bugs | <https://github.com/YoYoGames/GameMaker-Bugs> | ✅ |
| GMCLAN versiones | <https://gms-updates.gmclan.org/> | ✅ |
| YellowAfterlife Substack | <https://yellowafterlife.substack.com/> | ✅ |
| YellowAfterlife Blogspot | <http://yellowafterlife.blogspot.com/> | ✅ |
| YellowAfterlife itch.io | <https://yellowafterlife.itch.io/> | ✅ |
| Juju Adams web | <https://www.jujuadams.com/> | ✅ |
| Juju Adams GitHub | <https://github.com/jujuadams> | ✅ |
| **GameMakerLibraries** | <https://github.com/JujuAdams/GameMakerLibraries> | ✅ |
| Juju Adams itch.io | <https://jujuadams.itch.io/> | ✅ |
| DragoniteSpam itch.io | <https://dragonite.itch.io/> | ✅ |
| gm(48) developer blogs | <https://gm48.net/developer-blogs/> | ✅ |
| YouTube oficial | <https://www.youtube.com/@GameMakerEngine> | ✅ |
| GameDev.net | <https://www.gamedev.net/> | ⚠️ 403 a cliente automático; OK en navegador |
