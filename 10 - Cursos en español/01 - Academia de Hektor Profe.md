# 01 · Academia de GameMaker — Hektor Profe (Escuela de Videojuegos)

> **El curso de GameMaker en español más completo que existe.** 7 cursos · **100 lecciones**.
> Autor: **Héctor Costa Guzmán**. Licencia **CC BY 4.0** (2015-2022).
> Web: <https://hektorprofe.github.io/escueladevideojuegos/academia-gamemaker/>
> Verificado el 1 de septiembre de 2026.

---

## ⚠️ Lee esto antes de empezar

**Todo el material está hecho con GameMaker: Studio 1.4**, una versión **descatalogada** que
ya no se puede descargar de la web oficial. El propio autor lo advierte en la página y enlaza
una copia de seguridad compartida por un tercero.

**No instales GameMaker 1.4 para seguir estos cursos.** Instala LTS 2026 y usa la academia
como lo que es: **la mejor explicación en castellano de cómo se piensa un videojuego**,
traduciendo tú el código a GML moderno sobre la marcha.

### Qué sigue valiendo íntegro

- El **modelo mental**: room, sprite, objeto, instancia, evento. No ha cambiado.
- El **orden de eventos**: Create → Step → Collision → Draw → Draw GUI. Idéntico.
- Las **máquinas de estados**, la IA de persecución, el diseño de HUD, el uso de superficies
  para oscuridad y pausa, las partículas: la lógica es la misma.
- El **diseño de juego**: por qué un Breakout enseña colisiones y un Snake enseña estructuras.

### Qué está muerto y hay que reescribir

| En el curso (GMS 1.4) | En LTS 2026 | Dónde está explicado |
|---|---|---|
| `script_execute` y scripts sueltos | `function` con nombre, `method`, `static` | [`01 - Fundamentos/07`](../01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md) |
| `ds_list` / `ds_map` para todo | Arrays y **structs** (se limpian solos) | [`01 - Fundamentos/05`](../01%20-%20Fundamentos/05%20-%20Arrays%20y%20estructuras%20de%20datos.md) |
| Sin structs ni constructores | `constructor`, `new`, herencia con `:` | [`01 - Fundamentos/04`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) |
| `view_xview[0]`, `view_wview[0]` | **Cámaras** y viewports (`camera_*`) | [`01 - Fundamentos/10`](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) |
| `background_*` y recurso *background* | **Capas** de room (`layer_*`); el recurso ya no existe | [`01 - Fundamentos/10`](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) |
| `depth` para ordenarlo todo | **Layers** para organizar, `depth` solo dentro de una capa | [`01 - Fundamentos/10`](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) |
| IDs de assets como números | **Handles** — la aritmética con ellos está prohibida | [`01 - Fundamentos/03`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) |
| `room_speed` fijo | `delta_time` y *time sources* | [`01 - Fundamentos/06`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) |
| Tiles del editor antiguo | **Tile sets**, autotiles y `tilemap_*` | [`08 - Referencia GML/09`](../08%20-%20Referencia%20GML%20completa/09%20-%20Dibujo%20de%20tiles%20y%20tilemaps.md) |
| HUD dibujado a mano en Draw GUI | Sigue valiendo, pero hoy hay **UI Layers y Flexpanels** | [`02 - Novedades 2026/04`](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md) |
| `sound_play`, `sound_volume` | `audio_play_sound`, buses y efectos | [`02 - Novedades 2026/07`](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) |

> 🔧 **Método recomendado:** ve la lección, entiende el *porqué*, y escribe el código tú con
> GML de 2026 verificando cada función con `python3 "_indice/buscar.py" <función>`. Si una
> función del vídeo no aparece, es que la retiraron: el buscador te dirá cuál la sustituye.

---

## Los 7 cursos

Los vídeos están alojados en **Odysee** (el autor los migró desde YouTube). Cada curso tiene
un `.zip` con los recursos gráficos y de audio, enlazado desde su sección en la web.

### 1 · Tu Primer Videojuego — 19 lecciones · sin escribir código

Juego de una avioneta que esquiva bombas, hecho **solo con acciones de arrastrar y soltar**.

`01` Presentación · `02` Conceptos básicos de los videojuegos · `03` Instalación del programa ·
`04` Las Rooms, los Sprites y los Objetos · `05` Propiedades y Eventos de Objeto ·
`06` Animar un Sprite · `07` Fondo en movimiento y Sonidos · `08` Dibujar Textos y Sprites ·
`09` El Objeto Bomba · `10` Colisiones entre Objetos que chocan · `11` Crear el Objeto Explosión ·
`12` Hacer que el Avión Explote · `13` Evento Step y rastro de humo ·
`14` Cámara, Ventana, Views, Ports y Seguimiento · `15` Crear un Marcador usando Variables ·
`16` Condición de fin de juego y reinicio · `17` Un contacto con el GML ·
`18` Alarmas y Aleatoriedad · `19` Mejorar la experiencia final

> **Valor hoy: alto para el concepto, bajo para la práctica.** Las lecciones 04, 05, 13, 15,
> 16 y 18 explican el modelo mental de GameMaker mejor que casi nada en inglés. Las lecciones
> 03 y 14 están obsoletas (instalación y sistema de *views* antiguo).

### 2 · El Lenguaje GML — 17 lecciones · programación desde cero

`01` Variables y Literales · `02` Macros · `03` Operadores · `04` Expresiones ·
`05` Condiciones If y Switch · `06` Bucles Do, While, Repeat y For ·
`07` Scripts (definición y manejo) · `08` Funciones útiles · `09` Objetos e instancias ·
`10` Sprites y sus propiedades · `11` Evento Step · `12` Evento Draw · `13` Evento Draw GUI ·
`14` Inputs por teclado y ratón · `15` Cambios de Room · `16` Control de Alarmas ·
`17` Control de Sonido

> **Valor hoy: alto en 01-06 y 09-14** (la base del lenguaje no ha cambiado).
> **La lección 07 está obsoleta**: los *scripts* de GMS 1.4 ya no existen como concepto; hoy
> se declaran funciones dentro de un asset de script. **La 17 también**: el sistema de audio
> es otro.

### 3 · Serie de Minijuegos — 9 videotalleres

`01` Breakout · `02` Plataformas · `03` Horizontal Runner · `04` Vertical Shooter ·
`05` Defender la base · `06` Flappy Planes · `07` Buscar Parejas · `08` Carreras de coches ·
`09` Snake

> **Valor hoy: muy alto.** Nueve mecánicas distintas en formato corto. Es el mejor
> entrenamiento que hay en español para *lógica de juego 2D*, y encaja directamente con
> [`04 - Recetas por género`](../04%20-%20Recetas%20por%20g%C3%A9nero/), que te da la versión
> moderna de cada uno de esos sistemas.

### 4 · Juego Arcade PONG — 12 lecciones · primer juego completo

`01` Presentación · `02` Preparar recursos · `03` Room y objetos base · `04` Movimiento ·
`05` Colisiones paredes · `06` Colisiones jugador · `07` Gestionar dificultad ·
`08` Marcador de puntos · `09` Añadir los sonidos · `10` Portada con menú ·
`11` Mejorar portada · `12` Retoques y distribución

> **Valor hoy: alto.** Incluye lo que casi ningún tutorial cubre: **menú, dificultad
> progresiva y distribución**. La lección 07 (curva de dificultad) es la joya.

### 5 · Juego Shooter TDS — 25 lecciones · el curso grande ★

Un *top-down shooter* de supervivencia con zombis. **Es el mejor curso del catálogo.**

`01` Presentación · `02` Movimiento básico · `03` Fondo, vista y cámara ·
`04` Colisiones y máscaras · `05` Disparar desde el arma · `06` Estados y animaciones ·
`07` Estado de movimiento · `08` Estado de persecución · `09` Estado de ataque ·
`10` Ataques y colisiones · `11` Gestionar las vidas · `12` HUD: barra de vida y avatar ·
`13` Barra de vida en enemigos · `14` Fuego de disparo · `15` Sustituir cursor por mirilla ·
`16` Láser en el arma · `17` Música y sonidos · `18` Escenario con tiles ·
`19` Ajustes de máscaras y profundidad · `20` Partículas: efecto sangre ·
`21` Oscuridad con superficies · `22` Gestor de niveles con pilas y User Events ·
`23` HUD: marcador y nivel · `24` Pausar con superficies · `25` Golpe cuerpo a cuerpo

> **Valor hoy: muy alto.** Las lecciones **06-09** (máquina de estados para IA) y **21/24**
> (superficies para oscuridad y pausa) son técnicas que siguen siendo exactamente así en 2026.
> Compáralas con [`04 - Recetas/02 · Top-Down / Twin-Stick`](../04%20-%20Recetas%20por%20g%C3%A9nero/02%20-%20Top-Down%20_%20Twin-Stick.md)
> y con `06 - Assets y Scripts/scr_state_machine.gml`, que es la versión moderna con structs.
> ⚠️ La 20 (partículas) hay que rehacerla: el sistema de partículas cambió en 2026.

### 6 · Juego Action RPG — 13 lecciones ★

`01` Presentación · `02` Sprites y movimiento · `03` Máquina de estados ·
`04` Estado de ataque · `05` Diseño de escenario · `06` Gestión de colisiones y debug ·
`07` Teletransporte entre rooms · `08` Diálogos y HUD con zona · `09` Hierbas atacables ·
`10` Conejitos atacables · `11` Enemigos goblin atacables ·
`12` Corazones, vidas y reinicio de juego · `13` Sistema de guardado en INI y NPC

> **Valor hoy: muy alto.** Es el único curso en español que monta un **RPG de acción completo**
> con diálogos, NPCs y guardado. Cruzarlo con
> [`04 - Recetas/04 · RPG / Action RPG`](../04%20-%20Recetas%20por%20g%C3%A9nero/04%20-%20RPG%20_%20Action%20RPG.md).
> ⚠️ La lección 13 usa ficheros INI; hoy conviene JSON o buffers
> ([`01 - Fundamentos/14`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md),
> y `06 - Assets y Scripts/scr_save_load.gml`).

### 7 · Juego Beat'em Up — 5 lecciones

`01` Control de Animaciones · `02` Control de Movimientos · `03` Añadiendo los Enemigos ·
`04` Creando la Barra de Vida · `05` Creando las Escenas

> **Valor hoy: medio.** Es corto y se centra en una máquina de estados avanzada para
> animaciones. La lección 05 (planificación de enemigos por escenas) es la más útil.

---

## Contenido complementario de la misma web

La Escuela de Videojuegos tiene, además de la academia, artículos independientes del motor
que siguen siendo válidos al 100 %:

**Artículos destacados** · ¿Qué son los videojuegos? · ¿Cómo funcionan? · ¿Cómo se crean? ·
¿Cómo trabajar en el sector? · ¿Cómo mejorar los juegos 2D? · ¿Qué es el Motion Blur?

**Matemáticas y geometría para videojuegos** ★ · El eje de coordenadas · Funciones, sistemas
y puntos · Líneas (ecuaciones lineales) · Colisiones entre líneas · Distancia entre dos puntos ·
Parábolas · Círculos y esferas

> 💡 La serie de **matemáticas** es material atemporal y en español, y encaja directamente con
> [`08 - Referencia GML/10 · Matemáticas`](../08%20-%20Referencia%20GML%20completa/10%20-%20Matem%C3%A1ticas.md)
> y [`11 · Vectores, matrices y ángulos`](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores%2C%20matrices%20y%20%C3%A1ngulos.md).

**Recopilaciones de software** · 12 frameworks y librerías · 10 engines y motores ·
10 editores de audio · 8 editores gráficos 2D · 5 editores de mapas y fuentes ·
3 editores de modelaje 3D

---

## Licencia

**CC BY 4.0** — *2015-2022 © Héctor Costa Guzmán*. Puedes reutilizar y adaptar el material
citando la autoría. Es de las pocas fuentes en español con licencia explícitamente abierta.

## Fuentes

- Academia de GameMaker: <https://hektorprofe.github.io/escueladevideojuegos/academia-gamemaker/>
- Escuela de Videojuegos (índice): <https://hektorprofe.github.io/escueladevideojuegos/>
- Web personal del autor: <https://hektorprofe.net/>
