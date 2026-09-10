# Biblioteca GameMaker · para que tu agente de IA no invente funciones

> **El problema.** Le pides a un agente de IA que escriba GML y te devuelve
> `instance_create()`, `draw_set_blend_mode()` o `directory_get_working()`. Suenan bien. No
> existen. Descubres el error cuando el compilador falla — o peor, cuando no falla y el juego se
> comporta raro. GameMaker cambió de IDs numéricos a *handles* en 2026, retiró 171 funciones y
> reescribió el sistema de partículas, y el conocimiento que traen los modelos es de antes.
>
> **La solución.** Una base de conocimiento local, en español, que un agente consulta antes de
> escribir. Los símbolos no salen de una lista escrita a mano: se derivan del `GmlSpec.xml` **del
> runtime que tú tienes instalado**. Si `buscar.py` no la encuentra, no existe.

```sh
git clone https://github.com/SwonDev/gamemaker-biblioteca.git
cd gamemaker-biblioteca
./instalar.sh
```

Eso instala la skill (formato `SKILL.md`, el mismo que usa Claude Code) en cada CLI de IA que
tengas instalado — **Claude Code, Codex, opencode, Qwen Code, Kimi Code CLI**, más
`~/.agents/skills` (el estándar abierto [Agent Skills](https://agentskills.io) que además leen
**GitHub Copilot CLI, Gemini CLI y Cursor CLI**) — y genera los índices contra tu GameMaker. Si
detecta **Cline**, también lo instala en su carpeta de skills. Salta sin tocar nada los que no
tengas. A partir de ahí, cada agente la activa solo al hablar de GameMaker, GML o `.yyp` — no hace
falta invocarla a mano. Detalle completo, con fuentes, en
[«Qué CLI están soportados»](#qué-cli-de-ia-están-soportados) más abajo.

```sh
python3 _indice/buscar.py draw_sprite_ext     # firma exacta, ¿obsoleta?, manual, uso real
python3 _indice/buscar.py --todo "coyote time" # símbolos + documentación + manual + código
python3 _indice/validar-proyecto.py ~/MiJuego  # ¿hay funciones inventadas en mi proyecto?
python3 _indice/auditar-juego-completo.py ~/MiJuego  # ¿es un juego o solo un bucle de juego?
```

**Compatibilidad.** Desarrollado y probado a diario en macOS. Los scripts de `_indice/` son
Python puro y detectan la ruta de caché de `gm-cli` según el sistema operativo (macOS, Windows,
Linux) igual que hace la propia herramienta — pero **no verificado fuera de macOS**: si algo
falla en Windows o Linux, es un bug real, repórtalo. `instalar.sh` y `reconstruir.sh` son bash:
en Windows hace falta Git Bash o WSL (`cmd.exe`/PowerShell no valen); el resto de comandos
(`python3 _indice/buscar.py …`) funcionan igual en cualquier terminal. Herramientas externas que
se asumen en el PATH: `python3` (o `python`, si el sistema no registra el primero — común en
Windows), `git` (para `./reconstruir.sh codigo`), y `grep`/`curl` (de serie en macOS/Linux; en
Windows 10 1803+ `curl` viene incluido, `grep` no — instala Git for Windows o usa WSL). Sin
alguno de ellos, cada script lo dice explícitamente en vez de fallar con un traceback.

## Qué hay dentro

**272 documentos en español**, del `if` a cómo se firma una build para Steam. No solo el motor:
diseño de juego y GDD, niveles, pixel art, animación, VFX y shaders, UI y accesibilidad, cámaras,
arquitectura, generación procedural, físicas y fluidos, combate, IA, pathfinding, progresión,
sonido, narrativa, testing, producción y negocio. Y **59 recetas por género**, de plataformas a
*bullet heaven*.

**Herramientas que la mantienen honesta.** Un solo comando —`python3 _indice/actualizar.py`—
verifica los enlaces, regenera los índices, comprueba la ortografía, detecta funciones inventadas
en los ejemplos, prueba que un agente encuentra lo que necesita y compara el espejo del manual
español con el inglés. Sale con 0 solo si no queda deuda.

## Qué NO incluye, y por qué

El manual oficial y los 635 repositorios de código real que usa la versión completa **no se
redistribuyen aquí**: el manual es obra de YoYo Games, y cada repositorio tiene su licencia. Se
reconstruyen en tu máquina. Sin ellos, `buscar.py` sigue dando la firma exacta de cualquier
símbolo (sale del runtime), pero te remitirá a `manual.gamemaker.io` en vez de a un archivo local,
y las búsquedas `--codigo` no devolverán resultados. Para recuperar las dos cosas:

```sh
./reconstruir.sh manual   # descarga y convierte el manual oficial (≈6 150 páginas)
./reconstruir.sh codigo   # clona con git los repositorios libres catalogados (≈3,8 GB)
```

Ambos son reanudables y piden confirmación antes de empezar. El segundo excluye siempre los
juegos comerciales (Pizza Tower, Deltarune, AM2R, Hotline Miami, Kirby y cualquier otro sin
licencia libre en su categoría). Detalle completo, incluida la limitación conocida del
conversor del manual, en [`PUBLICAR.md`](./PUBLICAR.md).

**Versión de referencia:** GameMaker LTS 2026.0 · IDE 2026.0.0.16 · runtime GMS2 2026.0.0.23.
Licencias en [`LICENSE`](./LICENSE): MIT las herramientas, CC BY-SA 4.0 la documentación.
Proyecto independiente, sin relación con YoYo Games.

---

# Biblioteca de conocimiento · GameMaker LTS 2026

> **Puerta de entrada única** a toda la base de conocimiento de GameMaker de este repositorio.
> Última ampliación: **1 de septiembre de 2026** · **272 documentos propios en español**,
> **6 152 páginas de manual oficial espejado**, **la API completa del runtime** y
> **635 repositorios con 61 959 archivos `.gml`**. 3,8 GB · UTF-8.
> Versión de referencia: **GameMaker LTS 2026.0** (IDE 2026.0.0.16 · GMS2 Runtime 2026.0.0.23) ·
> Beta **2026.100.0** (IDE 1139 / runtime 1090) · **GMRT** en Beta 0.21.

> 🤖 **¿Eres un agente de IA?** Empieza por **[`AGENTS.md`](./AGENTS.md)**, no por aquí.
> Y antes de escribir una sola función: `python3 "_indice/buscar.py" <símbolo>`.

---

## 1. Qué es esto

Esta carpeta es una **biblioteca de referencia personal** para volverse experto en GameMaker.
No es un curso lineal: es un conjunto de materiales **organizados para consulta rápida**,
escritos en español y pensados para que los leas en el orden que te haga falta según tu
situación.

Contiene:

- **Manual traducido y reordenado** — los fundamentos de GML explicados con el «por qué», no solo el «qué».
- **Novedades de 2026 documentadas** — handles, GMRT, UI Layers, Flexpanels, Package Manager, roadmap.
- **44 capítulos de cursos de YouTube** transcritos, traducidos y reescritos como capítulos de curso.
- **15 recetas por género** — cómo se construye cada tipo de juego, sistema por sistema.
- **Referencia de publicación y tutoriales oficiales** — los 106 tutoriales oficiales catalogados.
- **El ecosistema completo** — repositorios verificados, librerías, extensiones, plantillas, comunidad.
- **Scripts GML listos para importar** — matemáticas, cámara, FSM, tweens, guardado, pooling, A*, input, debug.
- 🆕 **El manual oficial entero, sin conexión** — 3 119 páginas en inglés y 3 033 en español, en Markdown.
- 🆕 **La API completa del runtime** — 2 357 funciones, 886 constantes, 210 variables y 33 structs,
  extraídas del `GmlSpec.xml` del runtime instalado. Si algo no está ahí, **no existe**.
- 🆕 **635 repositorios descargados** — 61 959 archivos `.gml` reales, organizados por tema y catalogados en español.
- 🆕 **Cursos y recursos en español** — investigados, verificados uno a uno y con veredicto honesto.
- 🆕 **Utilidades e integraciones** — itch.io, extensiones nativas, Steam, Discord, Photon, Colyseus, pipeline de arte.
- 🆕 **Un buscador offline** — `_indice/buscar.py` cruza símbolo ↔ manual ↔ documentación ↔ código real.

Todo lo que aparece aquí se ha **verificado contra fuentes primarias**: el manual oficial
(`gm-cli manual read`), la API de GitHub, los READMEs de los repositorios y proyectos reales
creados con el CLI. Lo que **no** se ha podido verificar está marcado explícitamente con ⚠️.

**Regla de oro de toda la biblioteca:** los nombres de funciones, constantes y argumentos se
respetan **en inglés** (son la API real). Las explicaciones y los comentarios están en español.

---

## 2. Estado del ecosistema GameMaker hoy (1 de septiembre de 2026)

1. **LTS 2026.0 es la rama estable.** Publicada el 21 de mayo de 2026. IDE 2026.0.0.16, runtime GMS2 2026.0.0.23. Es la que debes usar para cualquier proyecto serio.
2. **El ciclo LTS va de 2026.0 a 2026.4**, con soporte hasta al menos el **Q1 de 2028**. Cada minor release sale aproximadamente cada seis meses y mantiene la compatibilidad.
3. **El runtime GMS2 está marcado como *feature complete*.** Ya no recibe características nuevas: sigue recibiendo actualizaciones de SDK y correcciones críticas, pero **todo lo nuevo se desarrolla para GMRT**.
4. **GMRT (GameMaker Runtime, nombre en clave *Cronus*) está en Beta 0.21.** Es el runtime nuevo: arquitectura abierta con CMake, LLVM/Clang, Dawn y SDL2. Se instala desde el **Package Manager**. Tiene una sección propia de *«Changes to GML»*: **no** es 100 % compatible con GMS2.
5. **Los Handles sustituyen a los IDs numéricos** de assets. Es el cambio que más código antiguo rompe, y lo hace en silencio. Léelo antes de portar nada.
6. **Llegan lenguajes nuevos**: JavaScript (Q2 2026), TypeScript (Q3 2026) y C# (Q4 2026) según el roadmap público.
7. **UI Layers y Flexpanels** (Yoga / flexbox) cambian la forma de hacer interfaces: se acabó el dibujar HUDs a mano en Draw GUI.
8. **Package Manager y Prefabs** hacen que la IDE sea modular: los assets, las extensiones y hasta el propio runtime se instalan como paquetes versionados.
9. **Feather (el analizador de tipos) está activado por defecto** y el Code Editor 2 está disponible en la Beta. El tipado con JSDoc deja de ser opcional si quieres un código limpio.
10. **Targets nuevos**: Nintendo Switch 2, Reddit (Devvit), Game Strips y Live Wallpapers en GX.games. Y **JS/TS/C# en camino** sobre GMRT.

11. 🆕 **El canal Monthly está discontinuado.** Lo sustituye LTS 2026; el último Monthly fue el **2024.14.4**. Hoy solo hay tres canales: **LTS** (estable), **Beta** y **GMRT**.
12. 🆕 **La Beta vigente es la 2026.100.0** (Release 5, IDE 1139 / runtime 1090, 27-08-2026), que corresponde al futuro **2026.1**. Trae el **Prefab Builder** (`#14754`), inyección de código en compilaciones de macOS desde el Editor de Extensiones (`#15809`) y un buen puñado de correcciones de estabilidad.
13. 🆕 **El multijugador dejó de ser el punto débil.** En julio salió la **extensión oficial de Photon** (salas, emparejamiento, chat de texto y **voz**) y en agosto la de **Colyseus** (servidor autoritativo de código abierto con API completa de GML). Además, **Fusion Core 3 de Photon llegará a GMRT como característica del núcleo**. Detalle en [`12 - Utilidades e integraciones/04`](./12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md).

> **Consecuencia práctica:** aprende y trabaja sobre **GMS2 Runtime** (es lo estable), pero escribe el código **pensando ya en GMRT**: sin IDs numéricos de assets, con structs, con manejo explícito de errores y sin dependencias de comportamientos deprecados.

---

## 3. Mapa de la biblioteca

| Carpeta | Archivos | Qué contiene | Para qué sirve |
|---|---:|---|---|
| [01 - Fundamentos](./01%20-%20Fundamentos/_INDICE-FUNDAMENTOS.md) | 18 | GML desde cero: tipos, handles, structs, arrays, eventos, movimiento, colisiones, instancias, rooms, dibujo, input, audio, persistencia, depuración | **Tu manual de cabecera.** El manual oficial reordenado, con el «por qué» explicado y las trampas marcadas |
| [02 - Novedades 2026](./02%20-%20Novedades%202026/_INDICE-NOVEDADES.md) | 11 | LTS 2026.0, cambios de GML, GMRT, UI Layers, partículas, gráficos, audio, Package Manager, Code Editor 2, roadmap | **Qué ha cambiado y hacia dónde va.** Imprescindible si vienes de 2023 o antes |
| [03 - Cursos (YouTube)](./03%20-%20Cursos%20%28YouTube%29/_INDICE-CURSOS.md) | 47 | 44 capítulos de curso transcritos + índice, enlaces originales y descubiertas | **Aprender haciendo.** Sky LaRell Anderson (12), DragoniteSpam (26), PixelatedPope cámaras (4), más el plataformas oficial |
| [04 - Recetas por género](./04%20-%20Recetas%20por%20g%C3%A9nero/_INDICE-RECETAS.md) | 59 | 15 géneros destripados sistema por sistema, el plano de un juego completo y 20 recetas transversales: game feel, señales, web, menús, ritmo, servicios, localización, Box2D, IA y árboles de comportamiento, luz, opciones, música, accesibilidad, móvil, 3D, combate cuerpo a cuerpo, 🆕 souls-like, metajuego transversal, party games, combate no letal | **Cómo se construye tu juego.** De plataformas a multijugador, y de 2D a 3D |
| [05 - Referencia](./05%20-%20Referencia/) | 6 | Tutoriales oficiales (106 catalogados), publicar y exportar, entregar el juego (firma/notarización/tiendas), 🆕 **publicar en consolas** (Nintendo/PlayStation/Xbox), **glosario A–Z**, **convenciones de estilo** | **Consulta rápida.** Lo que miras una vez y no memorizas |
| [06 - Assets y Scripts](./06%20-%20Assets%20y%20Scripts/README.md) | 11 `.gml` | Scripts reutilizables: matemáticas, cámara, FSM, tweens, guardado, pooling, A\*, input, debug | **Código para copiar.** Cada función verificada contra el manual |
| [07 - Ecosistema](./07%20-%20Ecosistema/_INDICE-ECOSISTEMA.md) | 24 | GitHub de YoYoGames, librerías, extensiones, proyectos de ejemplo, foro, itch.io, comunidades, blogs, GM CLI, IA | **El mundo alrededor del motor.** Qué usar, qué evitar y qué está abandonado |
| [08 - Referencia GML completa](./08%20-%20Referencia%20GML%20completa/) | 24 + API | Dibujo, formas, texto, color, superficies, shaders, vertex buffers, texturas, tiles, matemáticas, vectores, strings, DS, arrays, structs, buffers, ficheros, fecha, sistema · **+ el catálogo completo de la API** | **La referencia técnica en español**, tema por tema |
| 🆕 [09 - Manual oficial](./09%20-%20Manual%20oficial/README.md) | **6 152** | El manual oficial entero espejado: **3 119 páginas en inglés** y **3 033 en español, sin una sola página sin traducir** | **La fuente de verdad, sin conexión.** Cuando algo contradice a un tutorial, manda esto |
| 🆕 [10 - Cursos en español](./10%20-%20Cursos%20en%20espa%C3%B1ol/_INDICE-CURSOS-ES.md) | 13 | Todo el material de aprendizaje en castellano que existe, verificado con `yt-dlp`, con veredicto honesto, ruta de aprendizaje y apuntes completos de 17 vídeos transcritos | **Aprender sin pasar por el inglés** |
| 🆕 [11 - Código descargado](./11%20-%20C%C3%B3digo%20descargado/_CATALOGO.md) | **635 repos** | **61 959 archivos `.gml`** reales: 325 librerías por tema, 212 plantillas y ejemplos, 44 extensiones oficiales, 24 juegos y motores, 3 herramientas | **Ver cómo lo hace gente que ya lo ha hecho.** Todo greppable |
| 🆕 [12 - Utilidades e integraciones](./12%20-%20Utilidades%20e%20integraciones/_INDICE-UTILIDADES.md) | 10 | Herramientas de flujo de trabajo, extensiones nativas, Steam/Discord/Twitch, Photon y Colyseus, pipeline de arte y audio, itch.io, dónde buscar, tooling externo, 🆕 el manual del agente de IA para operar `gm-cli` | **Lo que rodea al motor y te hace ir más rápido** |
| 🆕 [13 - Diseño y producción de videojuegos](./13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/_INDICE-DISENO.md) | 28 | Diseño de juego (core loop, balance, dificultad, GDD), niveles, pixel art y resolución, animación (Sequences, Animation Curves), UI/UX, arquitectura del proyecto, generación procedural avanzada, físicas a mano y fluidos, sonido y mezcla, testing y QA, producción y lanzamiento, narrativa, matemáticas aplicadas, 🆕 formatos de producción especiales (kiosco, educativo, publicitario, infantil, *streaming*) | **El oficio de hacer juegos, no solo el motor.** Lo que va antes y alrededor del código, con GML verificado |
| 🆕 [_indice](./_indice/) | 5 + skill + memoria | `buscar.py` (buscador offline), `validar-proyecto.py` (valida el GML de un proyecto real), `actualizar.py` (mantenimiento en un comando), `simbolos.json` (3 486 símbolos), `documentos.json`, la skill [`skills/gamemaker-biblioteca/`](./_indice/skills/gamemaker-biblioteca/SKILL.md) — instalable en nueve CLI de IA distintos, ver [«Qué CLI están soportados»](#qué-cli-de-ia-están-soportados) —, y [`traduccion/`](./_indice/traduccion/README.md) (memoria de 4 503 frases y 2 009 celdas con la que se completó el manual en español) | **La forma rápida de encontrar cualquier cosa, desde aquí o desde otro proyecto** |

**Total: 272 documentos propios en español + 6 152 páginas de manual + 635 repositorios.**

### El buscador: úsalo antes que nada

```sh
python3 "_indice/buscar.py" move_and_collide       # ficha completa de un símbolo
python3 "_indice/buscar.py" --listar audio_        # toda una familia de funciones
python3 "_indice/buscar.py" --texto "coyote time"  # busca en la biblioteca en español
python3 "_indice/buscar.py" --manual "surface"     # busca en el manual oficial
python3 "_indice/buscar.py" --codigo "state"       # busca en 61 846 archivos .gml reales
```

La ficha de un símbolo te da la **firma exacta**, si está **obsoleta**, la **página del
manual en español y en inglés**, los **documentos de esta biblioteca** que lo explican y los
**repositorios reales** donde se usa. Si el símbolo no aparece, **no existe en este runtime**.

### Puntos de entrada rápida

| Necesito… | Voy a… |
|---|---|
| …empezar desde cero | [Ruta 0](#ruta-0--absoluto-principiante) |
| …entender por qué mi código antiguo falla | [Handles](./01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) |
| …un trozo de código concreto | [06 - Assets y Scripts](./06%20-%20Assets%20y%20Scripts/README.md) |
| …construir un juego de un género concreto | [04 - Recetas por género](./04%20-%20Recetas%20por%20g%C3%A9nero/_INDICE-RECETAS.md) |
| …saber si algo existe ya en GameMaker | `gm-cli manual read "<tema>"` |
| …una librería para input / texto / audio | [Librerías de la comunidad](./07%20-%20Ecosistema/02%20-%20Librer%C3%ADas%20esenciales%20de%20la%20comunidad.md) |
| …publicar en Steam / itch.io / móvil | [Publicar y exportar](./05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) |
| …publicar en Nintendo Switch, PlayStation o Xbox | [Publicar en consolas](./05%20-%20Referencia/06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md) |
| …un término que no entiendo | [Glosario GML](./05%20-%20Referencia/03%20-%20Glosario%20GML.md) |
| …las reglas de estilo de mi propio código | [Convenciones y estilo GML](./05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) |

---

## 4. Rutas de aprendizaje

> 🎓 **¿Quieres la progresión completa, de cero a profesional?** → **[RUTA.md](./RUTA.md)**
> Seis niveles con competencias observables, material exacto y una prueba por nivel.
> Las rutas de abajo son **puertas de entrada** según de dónde vengas; `RUTA.md` es el
> itinerario entero, incluido el tramo alto que estas no cubren.

Elige **una** según de dónde vengas. No las mezcles: cada una tiene un orden pensado.

---

### Ruta 0 · Absoluto principiante

> *Nunca he abierto GameMaker.* Objetivo: entender el modelo mental y tener un juego publicado.

**Fase 1 — Tocar la herramienta antes que la teoría (≈ 1 semana)**

| # | Haz esto | Archivo |
|---|---|---|
| 1 | Instala LTS 2026 y recorre el curso oficial de instalación | [Curso 40 · LTS 2026 — novedades e instalación](./03%20-%20Cursos%20%28YouTube%29/40%20-%20GameMaker%20LTS%202026%20-%20Novedades%20e%20Instalaci%C3%B3n.md) |
| 2 | Recorre el IDE: Asset Browser, Inspector, Output, editores | [01 · El IDE y el flujo de trabajo](./01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) |
| 3 | Capítulos 01 y 02 del curso principal: espacio de trabajo, objetos, sprites, rooms | [Curso 01](./03%20-%20Cursos%20%28YouTube%29/01%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%201%20-%20El%20Espacio%20de%20Trabajo.md) · [Curso 02](./03%20-%20Cursos%20%28YouTube%29/02%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%202%20-%20Objetos%2C%20Sprites%20y%20Rooms.md) |

**Fase 2 — Los cuatro conceptos que sostienen todo (≈ 2 semanas)**

| # | Tema | Archivo |
|---|---|---|
| 4 | Variables y tipos | [02 · Tipos de datos y variables](./01%20-%20Fundamentos/02%20-%20Tipos%20de%20datos%20y%20variables.md) |
| 5 | **Cuándo se ejecuta tu código** — el orden de eventos es el 80 % de los bugs de principiante | [06 · Eventos y ciclo del juego](./01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) |
| 6 | Instancias vs objetos, `with()`, herencia | [09 · Instancias, objetos y herencia](./01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) |
| 7 | Movimiento y colisiones | [08 · Movimiento y colisiones](./01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) |
| 8 | Refuerzo en vídeo: movimiento básico y plataformas | [Curso 03](./03%20-%20Cursos%20%28YouTube%29/03%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%203%20-%20Movimiento%20B%C3%A1sico%20y%20Colisiones.md) · [Curso 04](./03%20-%20Cursos%20%28YouTube%29/04%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%204%20-%20Movimiento%20de%20Plataformas.md) |
| 9 | ⚠️ **Pon Git en marcha YA**, antes de que tu proyecto valga algo | [Curso 24 · Control de versiones](./03%20-%20Cursos%20%28YouTube%29/24%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Control%20de%20Versiones%20con%20Git.md) |

**Fase 3 — Tu primer juego completo (≈ 3 semanas)**

Sigue los capítulos **05 → 12 del curso principal en orden**. El proyecto es acumulativo:
un juego cenital de un barco pirata que dispara, con enemigos, vida, puntuación, cámara,
música, fundidos entre habitaciones y un plataformas con salto variable. Acabas
publicándolo en **itch.io**.

[Curso 05 · Ratón y menús](./03%20-%20Cursos%20%28YouTube%29/05%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%205%20-%20Raton%20y%20Menus.md) →
[06 · Disparar proyectiles](./03%20-%20Cursos%20%28YouTube%29/06%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%206%20-%20Disparar%20Proyectiles.md) →
[07 · Cámaras](./03%20-%20Cursos%20%28YouTube%29/07%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%207%20-%20C%C3%A1maras.md) →
[08 · Enemigos y vida](./03%20-%20Cursos%20%28YouTube%29/08%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%208%20-%20Enemigos%20y%20Vida.md) →
[09 · Sonidos y música](./03%20-%20Cursos%20%28YouTube%29/09%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%209%20-%20Sonidos%20y%20M%C3%BAsica.md) →
[10 · Recursos de arte](./03%20-%20Cursos%20%28YouTube%29/10%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2010%20-%20Recursos%20de%20Arte.md) →
[11 · Animaciones y tile sets](./03%20-%20Cursos%20%28YouTube%29/11%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2011%20-%20Animaciones%20y%20Tile%20Sets.md) →
[12 · Exportar y publicar](./03%20-%20Cursos%20%28YouTube%29/12%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2012%20-%20Exportar%20y%20Publicar.md)

**Fase 4 — Consolida fundamentos y aprende las reglas de estilo**

| # | Tema | Archivo |
|---|---|---|
| 10 | Rooms, capas, cámaras, viewports | [10 · Rooms, capas, cámaras y viewports](./01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) |
| 11 | Dibujo y renderizado | [11 · Dibujo y renderizado](./01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) |
| 12 | Input | [12 · Input](./01%20-%20Fundamentos/12%20-%20Input%20-%20teclado%2C%20rat%C3%B3n%20y%20gamepad.md) |
| 13 | Persistencia | [14 · Persistencia y archivos](./01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) |
| 14 | ⚠️ **Las reglas de nombrado**, antes de que cojas vicios | [04 · Convenciones y estilo GML](./05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) |
| 15 | Depuración: el debugger, Feather y el Debug Overlay | [15 · Depuración y rendimiento](./01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) |

**Fase 5 — Ya eres peligroso. Ahora haz juegos.**

Salta a la [Ruta 3](#ruta-3--quiero-hacer-un-juego-ya) y elige un género.

> 💡 **No leas el capítulo 03 (Handles) al principio.** Léelo cuando te encuentres código de
> internet que usa IDs numéricos y no entiendas por qué falla.

---

### Ruta 1 · Vengo de otro motor

> *Unity, Godot, Construct, GameMaker en mis pesadillas.* Objetivo: traducir lo que ya sabes.

**Primero, las tres diferencias estructurales que te van a despistar:**

| Concepto | En Unity / Godot | En GameMaker |
|---|---|---|
| **Entidad** | `GameObject` + componentes / `Node` + scripts | **Objeto** (la plantilla) + **instancia** (la cosa viva). No hay componentes: el objeto *es* el script, el sprite y la máscara a la vez |
| **Escena** | `Scene` / `SceneTree` | **Room**. Las layers viven dentro de la room, no son objetos del árbol |
| **Ejecución** | `Update()` / `_process()` | **Eventos**: Create, Step, Draw, Collision… No hay un único `Update`; hay un orden de eventos fijo que **debes conocer** |
| **Colisiones** | `Rigidbody` + `Collider` + física | Máscaras de sprite + `place_meeting()` / `move_and_collide()`. La física es **opt-in** |
| **Profundidad** | Z / `z_index` | `depth` (legacy) o **layers** (moderno). Usa layers |

**Orden recomendado:**

| # | Tema | Archivo | Equivalencia que estás buscando |
|---|---|---|---|
| 1 | El IDE y el flujo de trabajo | [01 · Fundamentos](./01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) | Dónde está el *Project* panel, el *Inspector*, la *Console* |
| 2 | Tipos y variables | [02 · Fundamentos](./01%20-%20Fundamentos/02%20-%20Tipos%20de%20datos%20y%20variables.md) | Todo es `real` (double). Hay `int64`, `bool`, `struct`, `handle` |
| 3 | **Structs y constructores** | [04 · Fundamentos](./01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) | Tu «clase». `constructor` + `new`, herencia con `:` , `static` para miembros de clase |
| 4 | Funciones, métodos y ámbito | [07 · Fundamentos](./01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md) | `method()` ≈ lambda atada a un `self`. `static` ≈ miembro estático de C# |
| 5 | **Eventos y ciclo del juego** ⭐ | [06 · Fundamentos](./01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) | **El concepto más importante.** Aquí está tu `Update` |
| 6 | Instancias y herencia | [09 · Fundamentos](./01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) | `with()` ≈ iterar + ejecutar en el ámbito de otro objeto. Es potentísimo y no tiene equivalente directo |
| 7 | Movimiento y colisiones | [08 · Fundamentos](./01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) | `move_and_collide()` ≈ `CharacterController.Move()` |
| 8 | Rooms, capas, cámaras | [10 · Fundamentos](./01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) | Cámaras + viewports, no `Camera.main` |
| 9 | Dibujo | [11 · Fundamentos](./01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) | Sin `MeshRenderer`: todo es inmediato, se dibuja cada frame |
| 10 | ⚠️ **Handles** | [03 · Fundamentos](./01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) | No existen en otros motores. Un handle **no** es un int |
| 11 | Convenciones de estilo | [05 - Referencia 04](./05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) | Prefijos obligatorios, Feather y JSDoc |

**Atajos que te ahorran semanas:**

- **Tutorial oficial de plataformas en 15 min** → [Curso 39](./03%20-%20Cursos%20%28YouTube%29/39%20-%20GameMaker%20Oficial%20-%20Tu%20Primer%20Plataformas%20en%2015%20Minutos.md). El tour más rápido que existe.
- **Buenas prácticas de organización** → [01 · El IDE y el flujo de trabajo](./01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md).
- **Si vienes de Unity y quieres input serio**: no escribas el tuyo, usa [Input](./07%20-%20Ecosistema/02%20-%20Librer%C3%ADas%20esenciales%20de%20la%20comunidad.md) (Juju Adams, MIT).
- **Si vienes de Godot y quieres nodos/UI**: mira [UI Layers y Flexpanels](./02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md) — es lo más parecido a Control nodes.
- **Plantillas listas** para estudiar un proyecto ya montado → [06 · Plantillas y starters](./07%20-%20Ecosistema/06%20-%20Plantillas%20y%20starters.md).

> 💡 **Trampa nº 1 del que viene de fuera:** intentar hacer arquitectura de componentes en
> GameMaker. No la hagas. El modelo de GameMaker es objeto + eventos + structs para datos.
> Funciona bien si lo respetas y duele mucho si lo combates.

---

### Ruta 2 · Vengo de GameMaker antiguo

> *GMS 1.4 o GMS2 anterior a 2023.* Objetivo: que tu código viejo vuelva a compilar **y** que no se rompa en silencio.

⚠️ **Esta ruta empieza por donde duele.** No te la saltes.

| # | Cambio que te va a romper el código | Archivo |
|---|---|---|
| 1 | 🔴 **Los Handles sustituyen a los IDs numéricos.** `sprite_index + 1`, `asset_get_index()` con aritmética, comparar con `-1`… todo eso está muerto | [03 · Handles — el cambio clave de 2026](./01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) |
| 2 | 🔴 **Cambios en GML 2026**: comprobación de tipos, JSON, template strings, `string_ext()` | [02 · Cambios en GML 2026](./02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) |
| 3 | 🔴 **`instance_change()` y `position_change()` deprecadas** | [09 · Instancias, objetos y herencia](./01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) |
| 4 | 🟠 **Colisiones con bounding boxes precisos e inclusivos.** Hay modo de compatibilidad | [02 · Cambios en GML 2026](./02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) |
| 5 | 🟠 **Descarte automático de assets sin referenciar.** Rompe la carga dinámica clásica | [02 · Cambios en GML 2026](./02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) |
| 6 | 🟠 **Feather activado por defecto**: tu código viejo va a escupir cientos de avisos | [09 · Code Editor 2 y Feather](./02%20-%20Novedades%202026/09%20-%20Code%20Editor%202%20y%20Feather.md) |
| 7 | 🟡 **`ds_list` / `ds_map` frente a arrays y structs.** Ya casi nunca merecen la pena | [05 · Arrays y estructuras de datos](./01%20-%20Fundamentos/05%20-%20Arrays%20y%20estructuras%20de%20datos.md) |
| 8 | 🟡 **El GMS2 Runtime está *feature complete*.** Lo nuevo va a GMRT | [01 · Resumen LTS 2026.0](./02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md) |
| 9 | 🟡 **GMRT tiene su propia lista de cambios de GML.** No es drop-in | [03 · GMRT — El nuevo runtime](./02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md) |
| 10 | 🟢 **UI Layers**: deja de dibujar el HUD en Draw GUI | [04 · UI Layers y Flexpanels](./02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md) |
| 11 | 🟢 **Buses y efectos de audio** | [07 · Audio — buses y efectos](./02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) |
| 12 | 🟢 **Package Manager y Prefabs** | [08 · Package Manager y Prefabs](./02%20-%20Novedades%202026/08%20-%20Package%20Manager%20y%20Prefabs.md) |

**Checklist de migración, en orden de ejecución:**

```
1. Abre el proyecto en LTS 2026.0 y compila. Apunta TODOS los errores.
2. Activa Feather y revisa los avisos: son tu mapa de trabajo real.
3. Busca aritmética con IDs de assets   → grep: _index + | _index - | asset_get_index
4. Busca instance_change / position_change → reescribe con structs o crea/destruye
5. Busca ds_list / ds_map sin liberar   → migra a arrays/structs (se liberan solos)
6. Activa el Collision Compatibility Mode SOLO si las colisiones cambian de comportamiento
7. Marca con MarkTagAsUsed los assets que cargas dinámicamente
8. Migra el HUD a UI Layers (puede ser lo último)
9. Decide si vas a GMRT o te quedas en GMS2 Runtime (ver doc 03)
```

**Lo que ya NO debes escribir nunca más:**

```gml
// ❌ GMS 1.4 / GMS2 antiguo
var _next = sprite_index + 1;              // los handles no son números
instance_change(obj_enemigo_rapido, true); // deprecada
var _lista = ds_list_create();             // apenas necesario en 2026
if (room == rm_nivel_1) { ... }            // prefiere room_get_name() o handles
```

```gml
// ✅ GML moderno
var _frame = sprite_get_number(sprite_index);
var _siguiente = sprite_duplicate(sprite_index);   // o cambia el asset explícitamente
instance_destroy();
instance_create_layer(x, y, "Instances", obj_enemigo_rapido);
var _datos = { vida: 10, nombre: "slime" };        // struct: se limpia solo
```

---

### Ruta 3 · Quiero hacer un juego YA

> *Tengo una idea y quiero prototiparla esta semana.* Objetivo: el camino más corto a algo jugable.

**Paso 0 — Elige tu atajo (30 minutos):**

| Si tu juego es… | Empieza por la plantilla | Y lee la receta |
|---|---|---|
| Un plataformas | *Platformer* | [01 · Plataformas 2D](./04%20-%20Recetas%20por%20g%C3%A9nero/01%20-%20Plataformas%202D.md) |
| Un shooter cenital / twin-stick | *Twin Stick Shooter* | [02 · Top-Down / Twin-Stick](./04%20-%20Recetas%20por%20g%C3%A9nero/02%20-%20Top-Down%20_%20Twin-Stick.md) |
| Un shmup | *Scrolling Shooter* | [03 · Shoot 'em up](./04%20-%20Recetas%20por%20g%C3%A9nero/03%20-%20Shoot%20em%20up%20%28shmup%29.md) |
| Un survivor-like | *Survivor Game* | [09 · Survival y crafting](./04%20-%20Recetas%20por%20g%C3%A9nero/09%20-%20Survival%20y%20crafting.md) |
| Un tower defense | *Tower Defense* | [08 · Tower Defense](./04%20-%20Recetas%20por%20g%C3%A9nero/08%20-%20Tower%20Defense.md) |
| Un match-3 | *Match 3* | [07 · Puzzle y Match-3](./04%20-%20Recetas%20por%20g%C3%A9nero/07%20-%20Puzzle%20y%20Match-3.md) |
| Un juego de cartas | *Card Game* | [13 · Estrategia y gestión](./04%20-%20Recetas%20por%20g%C3%A9nero/13%20-%20Estrategia%20y%20gesti%C3%B3n.md) |
| Un arcade de un botón | *Fire Jump* · *Space Rocks* | [11 · Arcade y un botón](./04%20-%20Recetas%20por%20g%C3%A9nero/11%20-%20Arcade%20y%20juegos%20de%20un%20bot%C3%B3n.md) |
| Un endless runner | *Endless Runner* | [01 · Plataformas 2D](./04%20-%20Recetas%20por%20g%C3%A9nero/01%20-%20Plataformas%202D.md) |
| Un idle / incremental | *Idle Game* | [13 · Estrategia y gestión](./04%20-%20Recetas%20por%20g%C3%A9nero/13%20-%20Estrategia%20y%20gesti%C3%B3n.md) |

Crea el proyecto desde terminal (verificado):

```sh
gm-cli init --no-interactive -n mi-juego -t "Space Rocks" --ai --actions --toolchain GMS2@2026.0.0.23
```

> ⚠️ **Bug verificado el 31/08/2026 con `gm-cli` 2.3.0 en macOS.** Las plantillas que usan
> **prefabs** (por ejemplo *Platformer*) **fallan**:
> `Failed to restore project. "ProjectTool PREFABS RESTORE" exited with code 1`, y **no generan
> el `.yyp`**. No es cosa de la versión: ocurre igual en la 2.2.0 y en la 2.3.0, con y sin
> `--toolchain`. En cambio **sí funcionan** *Space Rocks* y *Blank Pixel Game* (probadas).
> **Solución rápida:** crea el proyecto con una plantilla que funcione (*Space Rocks* o
> *Blank Pixel Game*). **Y si necesitas justo una de las nueve, SÍ hay arreglo** —la causa es un
> `gmpm.dll` desparejado entre el CLI y el IDE, no la plantilla—: la receta de cuatro pasos,
> verificada ejecutándola, está en la
> [Trampa 1 de `12 · 09`](./12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md).
> El cuarto paso es el que falta en todas partes y sin él parece que el rodeo no sirve.
> Pruebas y detalle en
> [13 · GM CLI](./07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md).
> Para actualizar el CLI usa **npm** (`npm install -g @gamemaker/gm-cli@latest`), no pnpm: ya
> estaba gestionado con npm y mezclar gestores deja dos copias globales.

**Paso 1 — Copia los scripts base (5 minutos):**

Arrastra a tu proyecto los que necesites de [`06 - Assets y Scripts`](./06%20-%20Assets%20y%20Scripts/README.md):
`scr_math_util`, `scr_camera`, `scr_input_buffer`, `scr_debug`. Son independientes entre sí.

**Paso 2 — Sigue la receta de tu género:**

Cada receta te dice **qué sistemas construir y en qué orden**. Sigue el orden: está pensado
para que tengas algo jugable lo antes posible y vayas añadiendo profundidad después.

**Paso 3 — Añade *juice* desde el día 1:**

No lo dejes para el final. Lee [15 · Game feel y juice](./04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md)
en paralelo, desde la primera línea de código. Un movimiento con screen shake y squash &
stretch **parece** un juego; sin ellos parece una demo técnica.

**Paso 4 — Publica algo, aunque sea horrible:**

[Curso 12 · Exportar y publicar](./03%20-%20Cursos%20%28YouTube%29/12%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2012%20-%20Exportar%20y%20Publicar.md) →
[02 · Publicar y exportar](./05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) →
[08 · itch.io](./07%20-%20Ecosistema/08%20-%20itch.io%20-%20jams%2C%20assets%20y%20juegos.md)

> 💡 **El mejor acelerador que existe es una jam.** Busca una en [itch.io/jams](https://itch.io/jams)
> o apúntate a la siguiente [gm(48)](https://gm48.net/). Un plazo de 48 horas hace más por tu
> aprendizaje que un mes de teoría, porque **te obliga a recortar alcance**.

---

## 5. Los 10 conceptos que más rompen la cabeza

Ordenados por cuántas horas te van a costar si no los entiendes bien.

| # | Concepto | La confusión típica | Dónde se explica |
|---:|---|---|---|
| 1 | **Handles** | «¿Por qué `sprite_index + 1` ya no funciona?» Un handle **no** es un entero: es una referencia opaca validada por tipo. Los IDs se reciclan, los handles no mienten | [01 - Fundamentos/03](./01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) · [02 - Novedades/02](./02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) |
| 2 | **Structs vs instancias** | ¿Cuándo uso un objeto y cuándo un struct? Regla: **el struct guarda datos, el objeto hace cosas en el mundo** (eventos, colisiones, dibujo) | [01 - Fundamentos/04](./01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) · [09](./01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) · [Convenciones](./05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) |
| 3 | **`depth` vs layers** | `depth` es el sistema antiguo y convive mal con las layers. En 2026: **layers para organizar, `depth` solo para ordenar dentro de una capa de instancias** | [01 - Fundamentos/10](./01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) |
| 4 | **`delta_time` vs `room_speed`** | `room_speed` es cuántos *steps* por segundo quieres; `delta_time` es cuántos **microsegundos** han pasado de verdad. Si no multiplicas por `delta_time`, tu juego va más rápido en un monitor de 144 Hz | [01 - Fundamentos/06](./01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) |
| 5 | **Colisiones** | Máscara vs bounding box, `place_meeting` vs `instance_place`, por qué `move_and_collide()` necesita iteraciones, y qué es el *collision space* | [01 - Fundamentos/08](./01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) · [02 - Novedades/02](./02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) |
| 6 | **Cámaras y viewports** | La cámara es el «ojo» (ancho/alto/posición en la room); el viewport es el «marco» (dónde y cómo se dibuja en la ventana). Confundirlos = todo borroso o deformado | [01 - Fundamentos/10](./01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) · [Cursos 41–44](./03%20-%20Cursos%20%28YouTube%29/41%20-%20PixelatedPope%20-%20C%C3%A1maras%20y%20Resoluci%C3%B3n%202026%20-%20Parte%201%20-%20Principiante.md) · [Curso 36 (borroso)](./03%20-%20Cursos%20%28YouTube%29/36%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Por%20Qu%C3%A9%20Todo%20se%20ve%20Borroso.md) |
| 7 | **Surfaces y `application_surface`** | Una surface es una textura donde dibujas en vez de en pantalla. Si no existe cuando la usas, se pierde sin avisar (sobre todo al cambiar de pantalla completa). El `application_surface` es la surface donde se dibuja **todo** por defecto | [01 - Fundamentos/11](./01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) |
| 8 | **Asset compiler y descarte de assets** | El compilador descarta lo que no ve referenciado. Si cargas assets por nombre en tiempo de ejecución, **desaparecen** del build | [02 - Novedades/02](./02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) |
| 9 | **Garbage collector y memoria** | Los structs y arrays se limpian solos; las `ds_*`, las surfaces, los buffers y los **time sources** **no**. Y las instancias destruidas siguen «existentes» hasta el final del evento | [01 - Fundamentos/15](./01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) |
| 10 | **Game feel** | No es decoración: es la diferencia entre «funciona» y «se juega bien». Coyote time, jump buffering, screen shake, hit stop, squash & stretch | [04 - Recetas/15](./04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) · [01](./04%20-%20Recetas%20por%20g%C3%A9nero/01%20-%20Plataformas%202D.md) · [11](./04%20-%20Recetas%20por%20g%C3%A9nero/11%20-%20Arcade%20y%20juegos%20de%20un%20bot%C3%B3n.md) |

---

## 6. Cómo mantenerte al día

GameMaker se mueve rápido en 2026. Estas son las únicas fuentes que merecen tu atención:

| Fuente | URL | Frecuencia | Para qué |
|---|---|---|---|
| **Release notes** | <https://releases.gamemaker.io/> | Cada release | **La fuente de verdad.** Cambios de IDE y runtime, al detalle |
| **Blog oficial** | <https://gamemaker.io/en/blog> | Mensual | El «por qué» detrás de cada versión y los anuncios grandes |
| **Manual (LTS)** | <https://manual.gamemaker.io/lts/en/> | Continuo | Referencia de la rama estable |
| **Manual (Monthly)** | <https://manual.gamemaker.io/monthly/en/> | Continuo | Funciones más recientes. **Es el que consulta `gm-cli manual read`** |
| **Roadmap público** | <https://roadmap.gamemaker.io> | Trimestral | Qué viene y cuándo |
| **Rastreador de bugs** | <https://github.com/YoYoGames/GameMaker-Bugs> | Diario | ¿Es un bug conocido? Búscalo aquí antes de perder una tarde |
| **Foro oficial** | <https://forum.gamemaker.io/> | Diario | Dudas técnicas y la sección de tutoriales |
| **Discord oficial** | Ver [10 · Comunidades](./07%20-%20Ecosistema/10%20-%20Comunidades%20y%20d%C3%B3nde%20preguntar.md) | Diario | Respuestas rápidas y comunidad en español |
| **GMRT Beta** | <https://github.com/YoYoGames/GMRT-Beta> | Mensual | Seguimiento del runtime nuevo |
| **Redes oficiales** | [@GameMakerEngine](https://www.youtube.com/@GameMakerEngine) | Semanal | Vídeos cortos y directos |

**Rutina recomendada (15 minutos a la semana):**

```
1. releases.gamemaker.io → mira qué hay nuevo desde tu última versión
2. Si algo afecta a tu proyecto → gm-cli manual read "<función>"
3. Si algo huele a bug → busca en GameMaker-Bugs
4. Si vas a actualizar de minor LTS → lee primero el blog, no los release notes
```

---

## 7. Cómo usar esto con un agente de IA

Esta biblioteca está pensada para que **tú y un agente** trabajéis sobre ella. Estas son las
reglas que hacen que funcione:

> 📄 **El contrato completo está en [`AGENTS.md`](./AGENTS.md).** Esta sección es el resumen.

### Lo que el agente debe hacer siempre

1. **Leer [`AGENTS.md`](./AGENTS.md) antes de nada.** Y los archivos de contexto que haya en el
   repo donde vaya a trabajar: `CLAUDE.md`, `DESIGN.md`, `CONTEXT.md`. Si existen, mandan sobre
   cualquier recomendación genérica.
2. **Invocar la skill `gamemaker-expert`** antes de escribir una sola línea de GML.
3. **Verificar cada símbolo antes de usarlo, con el buscador local:**

   ```sh
   python3 "_indice/buscar.py" move_and_collide
   python3 "_indice/buscar.py" time_source_create
   ```

   Sale de `GmlSpec.xml` del runtime **realmente instalado**: 2 357 funciones, 886 constantes,
   210 variables. **Si no aparece, no existe.** El buscador sugiere alternativas parecidas y
   avisa de las **171 funciones obsoletas**.

4. **Contrastar con el manual** cuando necesites el detalle completo:

   ```sh
   gm-cli manual read "move_and_collide"          # el CLI oficial (rama monthly)
   python3 "_indice/buscar.py" --manual "surface" # el espejo local (rama LTS, es + en)
   ```

5. **Mirar cómo lo resuelve gente real** antes de inventarse una arquitectura:

   ```sh
   python3 "_indice/buscar.py" --codigo "coyote"
   ```

   Hay 61 846 archivos `.gml` de 608 repositorios reales.

### 🚫 Lo que el agente NO debe hacer nunca

- **NO editar archivos `.yy` ni `.yyp` a mano.** Su formato es frágil y se corrompe. Los recursos (objetos, sprites, rooms, eventos) se crean con el MCP `gamemaker-resource-tool` o con `gm-cli resourcetool eval "<comando>"`.
- **NO suponer una firma de función.** «Creo que era así» no es una fuente: está `buscar.py`.
- **NO usar funciones obsoletas.** Hay 171 marcadas; el buscador te avisa.
- **NO hacer aritmética con IDs de assets.** En 2026 son *handles*.
- **NO copiar código de los juegos comerciales extraídos** (Pizza Tower, Deltarune, AM2R, Hotline Miami, Kirby): están para leer, no son libres.
- **NO dar por buena la salida de otro agente** sin contrastarla si es decisiva.
- **NO usar `npm`**: el gestor es **`pnpm`**.

### El MCP de GameMaker es POR PROYECTO

El servidor MCP `gamemaker-resource-tool` **no es global**: exige un `.yyp` y se cierra al
arrancar si estás fuera de un proyecto.

```sh
# Proyecto nuevo (ya trae su .mcp.json)
gm-cli init -n mi-juego -t "Space Rocks" --ai

# Proyecto existente
gm-mcp-setup .
```

Si el MCP no está disponible en la sesión, **usa `gm-cli resourcetool eval`**: hace exactamente
lo mismo por terminal.

### Comandos que resuelven el 90 % de los casos

```sh
gm-cli init            # proyecto nuevo, con andamiaje de IA
gm-cli run             # ejecutar
gm-cli compile         # compilar
gm-cli package         # empaquetar
gm-cli manual read "tema"   # manual oficial offline ← la fuente de verdad
gm-cli resourcetool eval "<comando>"
gm-cli resourcetool repl
gm-cli resourcetool mcp
python3 "_indice/validar-proyecto.py" <ruta-del-proyecto>   # ¿inventé alguna función? antes de compilar
python3 "_indice/auditar-juego-completo.py" <ruta>          # ¿falta el menú, la pausa, el guardado?
```

Para fijar el runtime de esta biblioteca: `--toolchain GMS2@2026.0.0.23`.

### Desde otro proyecto: la skill `gamemaker-biblioteca`

Cada CLI de la tabla de abajo carga la skill `gamemaker-biblioteca` (en
`_indice/skills/gamemaker-biblioteca/`, instalada por `./instalar.sh` en la carpeta de skills de
cada uno) cuando la tarea huele a GameMaker. La skill les dice dónde está esta biblioteca, cómo
verificar cada símbolo, en qué orden leer cada disciplina (`references/mapa-disciplinas.md`) y qué
está prohibido. Su índice de documentos se regenera con `actualizar.py`, que además comprueba que
ninguna ruta citada se haya roto.

### Qué CLI de IA están soportados

Investigado en vivo contra documentación oficial el 07-09-2026 (no contra memoria de un modelo:
cada fila cita su fuente). Casi todos convergen hoy en el mismo formato de Claude Code —
una carpeta con `SKILL.md` (frontmatter YAML `name` + `description`) que el CLI descubre y activa
solo cuando la tarea encaja — así que `./instalar.sh` instala de más sin que moleste: cada CLI
decide cuándo usarla.

| CLI | Directorio de skills que instala `./instalar.sh` | Fuente |
|---|---|---|
| **Claude Code** | `~/.claude/skills/` | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| **Codex** (OpenAI) | `~/.codex/skills/` (funciona; un mantenedor de OpenAI la describe como *legacy*) y `~/.agents/skills/` (ruta **canónica** documentada hoy) | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) |
| **opencode** | `~/.config/opencode/skills/` — además lee `~/.claude/skills` y `~/.agents/skills` directamente, sin copiarlos | [opencode.ai/docs/skills](https://opencode.ai/docs/skills) |
| **Qwen Code** (Alibaba) | `~/.qwen/skills/` | [github.com/QwenLM/qwen-code · docs/users/features/skills.md](https://github.com/QwenLM/qwen-code/blob/main/docs/users/features/skills.md) |
| **Kimi Code CLI** (Moonshot) | `~/.kimi-code/skills/` (además lee `~/.agents/skills`) | [moonshotai.github.io/kimi-code/…/skills.html](https://moonshotai.github.io/kimi-code/en/customization/skills.html) |
| **Gemini CLI** (Google) | `~/.gemini/skills/` (alias `~/.agents/skills`) | [github.com/google-gemini/gemini-cli/docs/cli/skills.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md) |
| **GitHub Copilot CLI** | `~/.copilot/skills/` (alias `~/.agents/skills`) | [docs.github.com/…/copilot-cli/…/add-skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) |
| **Cursor CLI** (`cursor-agent`) | `~/.cursor/skills/` (alias `~/.agents/skills`; también lee `~/.claude/skills` y `~/.codex/skills`) | [cursor.com/docs/skills](https://cursor.com/docs/skills) |
| **Cline** (CLI oficial) | `~/.cline/skills/` | [docs.cline.bot/customization/skills](https://docs.cline.bot/customization/skills) |

`~/.agents/skills/` es el directorio genérico del estándar abierto
[Agent Skills](https://agentskills.io) (origen Anthropic): una sola copia ahí sirve para varios
CLI a la vez, incluso los que instales más adelante.

**Quedan fuera, investigados y sin soporte de skills instalable:**

- **GLM / Zhipu (Z.ai)** no tiene un CLI de terminal propio y dedicado. Su «GLM Coding Plan» se
  usa *dentro* de Claude Code, Codex, Cline u opencode (apuntando su endpoint a la API de
  Zhipu) — herramientas ya cubiertas arriba, con independencia del modelo que tengan detrás. Su
  producto propio, **ZCode**, es una app de escritorio Electron con terminal embebida, no un
  binario de terminal: fuera del alcance de este script.
- **Aider** no tiene directorio de skills propio (solo un paquete de terceros no oficial) ni
  confirma leer `AGENTS.md` en su documentación oficial. Si `./instalar.sh` lo detecta instalado,
  no le toca ningún archivo: te señala el `AGENTS.md` generado (ver abajo) para que lo referencies
  a mano con la clave `read:` de tu `.aider.conf.yml`.

**Si tu CLI solo entiende `AGENTS.md`** en la raíz de un proyecto (y no un directorio de skills):
`_indice/sincronizar-skill.py` deriva automáticamente
[`_indice/skills/gamemaker-biblioteca/AGENTS.md`](./_indice/skills/gamemaker-biblioteca/AGENTS.md)
del cuerpo real de `SKILL.md` — nunca se escribe a mano, así que no se desincroniza. Cópialo o
enlázalo como `AGENTS.md` en la raíz de ese proyecto de GameMaker.

### Cómo pedirle trabajo al agente

Las peticiones que mejor funcionan son las que **nombran archivos concretos de esta biblioteca**:

```
«Implementa una cámara con deadzone siguiendo 06 - Assets y Scripts/scr_camera.gml.
Verifica cada función con gm-cli manual read antes de escribirla.
Compila con gm-cli compile y no des la tarea por terminada hasta que compile sin errores.»
```

```
«Voy a portar este proyecto de GMS2 2023 a LTS 2026. Lee primero
01 - Fundamentos/03 - Handles.md y 02 - Novedades 2026/02 - Cambios en GML 2026.md,
luego hazme el checklist de migración de MI proyecto.»
```

```
«Quiero hacer un metroidvania. Lee 04 - Recetas por género/06 - Metroidvania.md
y dime qué sistemas necesito y en qué orden construirlos.»
```

### Referencia completa

- [13 · GM CLI — la línea de comandos](./07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md) — todos los subcomandos documentados.
- [14 · IA y GameMaker](./07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md) — estado real de la IA en 2026: **el motor no tiene IA**, `GMEXT-MLKit` es la única oficial, y el andamiaje `--ai` de `gm-cli init` **sí** funciona y genera `AGENTS.md`, `CLAUDE.md`, `.claude/` y `.mcp.json`.

---

## 8. Convenciones de toda la biblioteca

- Todos los archivos en **UTF-8**, español con tildes, eñes y signos de apertura (¿ ¡).
- Los bloques de código van marcados como ```gml y comentados en español.
- Los nombres de funciones, constantes y argumentos se respetan **en inglés**.
- Cada documento cierra con una sección de **fuentes** con las URLs originales.
- Lo no verificado se marca con ⚠️ en el cuerpo del texto y se recopila al final del índice de su carpeta.

### Iconos usados

| Icono | Significado |
|---|---|
| ⚠️ | Advertencia, trampa o error común |
| 💡 | Consejo práctico |
| ⭐ | Recomendación oficial del manual |
| 🆕 | Novedad relevante de versiones recientes |
| 🔴 | Te va a romper el código |
| 🟠 / 🟡 / 🟢 | Impacto alto / medio / bajo |
| ✅ / ❌ | Código correcto / incorrecto |

---

## 9. Fuentes primarias de toda la biblioteca

| Fuente | URL |
|---|---|
| Manual oficial (LTS) | <https://manual.gamemaker.io/lts/en/> |
| Manual oficial (Monthly) | <https://manual.gamemaker.io/monthly/en/> |
| Release notes | <https://releases.gamemaker.io/> |
| Blog oficial | <https://gamemaker.io/en/blog> |
| Roadmap | <https://roadmap.gamemaker.io> |
| Rastreador de bugs | <https://github.com/YoYoGames/GameMaker-Bugs> |
| GM CLI (npm) | <https://www.npmjs.com/package/@gamemaker/gm-cli> |
| GMRT Beta | <https://github.com/YoYoGames/GMRT-Beta> |
| LTS 2026.0: New Features, GMRT and Much More (21/05/2026) | <https://gamemaker.io/en/blog/lts-2026-release> |
| GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future (30/04/2026) | <https://gamemaker.io/en/blog/update-spring-2026> |
| Foro oficial | <https://forum.gamemaker.io/> |
| Tutoriales oficiales | <https://gamemaker.io/en/tutorials> |

---

*Biblioteca de conocimiento de GameMaker · Generada en agosto de 2026 · GameMaker LTS 2026.0 · UTF-8*
