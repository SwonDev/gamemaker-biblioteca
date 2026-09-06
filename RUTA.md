# 🎓 Ruta completa: de cero a experto

> **El itinerario maestro de esta biblioteca.** De no haber abierto GameMaker nunca a dirigir
> un proyecto comercial. Seis niveles, cada uno con **competencias observables**, material
> exacto y una prueba para saber si ya lo tienes.
>
> Las [rutas del README](./README.md#4-rutas-de-aprendizaje) son **puertas de entrada** según
> de dónde vengas. Esta es **la progresión completa**, y cubre además el tramo alto que
> aquellas no llegan a tocar.

---

## Cómo usar este documento

**Si eres una persona:** localiza tu nivel con la prueba de entrada, haz ese nivel entero y
vuelve. No saltes niveles: cada uno asume el anterior.

**Si eres un agente (Claude Code, Codex…):** usa la tabla de abajo para situar al usuario por
lo que *sabe hacer*, no por lo que dice saber. Después dale **solo el material de su nivel y
el siguiente**. Dar material de nivel 4 a alguien de nivel 1 es la forma más rápida de
bloquearlo.

| Nivel | Sabe hacer | Tiempo típico |
|---|---|---|
| **0 · Cero** | Nada. No ha instalado GameMaker | — |
| **1 · Aprendiz** | Mueve un personaje, detecta colisiones, cambia de room | 2-4 semanas |
| **2 · Autónomo** | Termina y publica un juego pequeño sin seguir un tutorial | 2-3 meses |
| **3 · Competente** | Elige arquitectura, depura solo, lee código ajeno | 6-12 meses |
| **4 · Avanzado** | Shaders, optimización medida, herramientas propias | 1-2 años |
| **5 · Profesional** | Dirige un proyecto comercial de principio a fin | 2+ años |

> ⚠️ **Los tiempos son orientativos y suponen práctica real.** Leer no cuenta. El único
> indicador fiable es **qué juegos has terminado**.

---

# Nivel 0 → 1 · Aprendiz

**Objetivo:** que la herramienta deje de ser un misterio.

### Qué tienes que saber hacer al terminar

- [ ] Crear sprite, objeto y room, y poner el objeto en la room
- [ ] Mover un personaje con el teclado
- [ ] Detectar una colisión y que pase algo
- [ ] Cambiar de room
- [ ] Entender **por qué** el código del evento Step se ejecuta 60 veces por segundo

### Material, en orden

1. [40 · LTS 2026 — novedades e instalación](./03%20-%20Cursos%20%28YouTube%29/40%20-%20GameMaker%20LTS%202026%20-%20Novedades%20e%20Instalaci%C3%B3n.md)
2. [01 · El IDE y el flujo de trabajo](./01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) — o, en vídeo y en español, [11 · Recorrido por el IDE](./10%20-%20Cursos%20en%20español/11%20-%20El%20IDE%20de%20GameMaker%20en%20español%20-%20recorrido%20guiado.md)
3. **En español:** [09 · Plataformas para principiantes](./10%20-%20Cursos%20en%20español/09%20-%20Plataformas%20para%20principiantes%20-%20apuntes%20de%20Alas%20de%20reptil%202025.md) — es el material más reciente que existe en castellano
4. [02 · Tipos de datos y variables](./01%20-%20Fundamentos/02%20-%20Tipos%20de%20datos%20y%20variables.md)
5. ⭐ [06 · Eventos y ciclo del juego](./01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) — **el concepto que más bugs de principiante evita**

### 🎯 Prueba de nivel

Haz un **Pong** sin mirar ningún tutorial. Dos palas, una bola, marcador, y que se pueda
volver a jugar sin cerrar. Si lo terminas, eres nivel 1.

### Errores que vas a cometer

| Error | Por qué pasa | Dónde está la respuesta |
|---|---|---|
| «Mi animación no avanza» | Asignas `sprite_index` cada frame | [Máquina de estados de animación](./10%20-%20Cursos%20en%20español/08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md#3--máquina-de-estados-de-animación) |
| «El personaje pega un salto al girarse» | El origen del sprite no está centrado | [Sprites y origen](./10%20-%20Cursos%20en%20español/09%20-%20Plataformas%20para%20principiantes%20-%20apuntes%20de%20Alas%20de%20reptil%202025.md#1--antes-del-código-sprites-origen-y-room) |
| «Salta infinitas veces en el aire» | No compruebas suelo antes de saltar | mismo documento, sección 3 |
| «Variable no existe» al cambiar de room | La creaste en Step, no en Create | [06 · Eventos](./01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) |

---

# Nivel 1 → 2 · Autónomo

**Objetivo:** terminar cosas. Es el salto donde más gente se queda.

### Qué tienes que saber hacer al terminar

- [ ] Escribir tus propias funciones y reutilizarlas
- [ ] Guardar y cargar la partida
- [ ] Montar un menú y una pantalla de pausa
- [ ] Usar Git sin que te dé miedo
- [ ] **Publicar un juego en itch.io**

### Material, en orden

1. [07 · Funciones, métodos y ámbito](./01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md)
2. [09 · Instancias, objetos y herencia](./01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) — aquí aprendes `with()`, la instrucción más infrautilizada
3. [08 · Movimiento y colisiones](./01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md)
4. [10 · Rooms, capas, cámaras y viewports](./01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md)
5. [14 · Persistencia y archivos](./01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md)
6. ⚠️ [04 · Convenciones y estilo GML](./05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — **antes de coger vicios**
7. [16 · Exportar y publicar](./01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md)
8. El curso completo en vídeo, capítulos 05→12: [Curso 2026 de Sky LaRell Anderson](./03%20-%20Cursos%20%28YouTube%29/_INDICE-CURSOS.md)

### 🎯 Prueba de nivel

**Termina y publica un juego pequeño en itch.io.** Que tenga menú, un nivel jugable, condición
de victoria y de derrota. No importa que sea feo. Importa que **esté terminado y publicado**.

> 💡 **El consejo más repetido de toda esta biblioteca:** haz una **game jam de 48 horas**
> ([gm(48)](./07%20-%20Ecosistema/08%20-%20itch.io%20-%20jams%2C%20assets%20y%20juegos.md)). Te obliga
> a recortar alcance, que es exactamente la habilidad que separa el nivel 1 del 2.

---

# Nivel 2 → 3 · Competente

**Objetivo:** dejar de copiar soluciones y empezar a elegirlas.

### Qué tienes que saber hacer al terminar

- [ ] Elegir entre varias formas de resolver algo y justificar por qué
- [ ] Depurar con el debugger, no con `show_debug_message` a ciegas
- [ ] Leer un proyecto ajeno y entender su arquitectura
- [ ] Montar una máquina de estados sin copiarla
- [ ] Saber cuándo **no** usar una librería

### Material, en orden

1. ⭐ [04 · Structs y constructores (POO en GML)](./01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)
2. ⭐ [03 · Handles — el cambio clave de 2026](./01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) — léelo cuando código de internet te falle sin motivo aparente
3. [05 · Arrays y estructuras de datos](./01%20-%20Fundamentos/05%20-%20Arrays%20y%20estructuras%20de%20datos.md)
4. [15 · Depuración y rendimiento](./01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)
5. ⭐ [16 · Señales y desacoplamiento](./04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md) — en cuanto tengas 3+ sistemas que reaccionan a lo mismo
6. [08 · Megaman X — un plataformas completo](./10%20-%20Cursos%20en%20español/08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md) — colisión por ejes, el patrón bueno
7. Tu género en [04 · Recetas por género](./04%20-%20Recetas%20por%20género/_INDICE-RECETAS.md)
8. [15 · Game feel y juice](./04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) — lo que separa «funciona» de «se siente bien»

### 🎯 Prueba de nivel

Coge un proyecto de [`11 - Código descargado`](./11%20-%20Código%20descargado/_CATALOGO.md) que
**no** hayas visto —`tldr-engine` o `Harmony-Framework`, ambos MIT— y explica en un párrafo
cómo está organizado y por qué. Si puedes, eres nivel 3.

### Lo que de verdad hace el código profesional

Antes de decidir arquitectura, lee el análisis de **1,3 millones de líneas de GML real**:
[15 · Qué hacen de verdad los proyectos reales](./07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md).

Te va a ahorrar discusiones: el motor de físicas integrado lo usa **1 proyecto de 21**, y
`delta_time` menos de la mitad.

---

# Nivel 3 → 4 · Avanzado

**Objetivo:** hacer cosas que la mayoría no sabe hacer, y medirlas.

### Qué tienes que saber hacer al terminar

- [ ] Escribir un shader propio y saber cuándo compensa
- [ ] Optimizar **con datos**, no por intuición
- [ ] Construir herramientas internas para tu propio proyecto
- [ ] Trabajar con surfaces, buffers y renderizado avanzado
- [ ] Automatizar tu compilación

### Material

| Tema | Dónde |
|---|---|
| **Shaders** | [11 · Dibujo y renderizado](./01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) · librerías del tema `shaders` en el [catálogo](./11%20-%20Código%20descargado/_CATALOGO.md) · **`Shady.gml`** para `#include` en GLSL |
| **Rendimiento medido** | [15 · Depuración y rendimiento](./01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) — Debug Overlay y perfilado |
| **Surfaces y buffers** | Los usan **21/21** proyectos reales. [Análisis del corpus](./07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md) |
| **Herramientas propias** | **`Emu`** (UI tipo Windows Forms) y **`gooey`**, ambas descargadas |
| **Línea de comandos y CI** | [13 · GM CLI](./07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md) |
| **Novedades de 2026** | [02 · Novedades 2026](./02%20-%20Novedades%202026/) — UI Layers, Flex Panels, GMRT |

### 🎯 Prueba de nivel

Coge un juego tuyo que vaya a 60 fps y **haz que vaya a 60 fps con el triple de entidades**.
Documenta qué mediste, qué cambiaste y cuánto ganaste. Si el «cuánto ganaste» sale de una
medición y no de una sensación, eres nivel 4.

---

# Nivel 4 → 5 · Profesional

**Objetivo:** que el problema deje de ser técnico.

A partir de aquí lo que te frena no es GML. Es alcance, tiempo, dinero y gente.

### Qué tienes que saber hacer

- [ ] Estimar y **recortar** alcance con criterio
- [ ] Sostener un proyecto grande durante meses sin que se pudra
- [ ] Portar a varias plataformas
- [ ] Trabajar con artistas y músicos
- [ ] Publicar comercialmente y sobrevivir al lanzamiento

### Material

| Tema | Dónde |
|---|---|
| **Arquitectura a escala** | Estudia `Pixel-Composer` (342 k líneas, MIT) y `ChapterMaster` (136 k) |
| **Multiplataforma** | [16 · Exportar y publicar](./01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) · preferencias por plataforma del manual |
| **Multijugador** | [14 · Multijugador](./04%20-%20Recetas%20por%20género/14%20-%20Multijugador.md) · `Gang-Garrison-2` (MPL) y `nt-recreated-public` (GPL) |
| **Pipeline de arte y audio** | [05 · Pipeline](./12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte%2C%20audio%20y%20niveles.md) · **AseSync** para no reimportar sprites a mano |
| **Integraciones comerciales** | [03 · Integraciones con servicios](./12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md) — Steam, tiendas, analítica |
| **Localización** | Librerías del tema `localizacion` en el catálogo |
| **Negocio y comunidad** | [11 · Blogs, newsletters y podcasts](./07%20-%20Ecosistema/11%20-%20Blogs%2C%20newsletters%20y%20podcasts.md) — post-mortems reales |

### La verdad incómoda sobre «triple A»

**GameMaker no hace juegos triple A**, y eso no es un defecto. Un triple A son cientos de
personas, motores propios y presupuestos de decenas de millones.

Lo que GameMaker sí ha hecho es una lista extraordinaria de **éxitos comerciales**:
*Undertale*, *Hotline Miami*, *Katana ZERO*, *Nuclear Throne*, *Risk of Rain*, *Hyper Light
Drifter*, *Pizza Tower*, *Forager*, *Chicory*, *Nidhogg*, *Downwell*. Varios de un solo autor.

**Ese es el techo real y es altísimo.** Si tu objetivo es vivir de tus juegos, GameMaker te
llega de sobra. Si tu objetivo es trabajar en un estudio triple A, el camino es C++ y Unreal, y
esta biblioteca no es la herramienta.

> 💡 **El mejor uso del nivel 5:** estudia los post-mortems de esos juegos. Casi todos cuentan
> la misma historia — el problema nunca fue el motor.

---

## Referencia rápida: dónde está cada cosa

| Necesito… | Voy a… |
|---|---|
| Comprobar que una función existe | `python3 "_indice/buscar.py" <nombre>` |
| La página del manual **en español** | `09 - Manual oficial/manual-lts-2026-es/` (completo, 0 páginas en inglés) |
| Una receta de mi género | [04 · Recetas por género](./04%20-%20Recetas%20por%20género/_INDICE-RECETAS.md) |
| Código real que ya funciona | [11 · Código descargado](./11%20-%20Código%20descargado/_CATALOGO.md) — 324 repos |
| Una librería que me ahorre trabajo | [12 · Utilidades](./12%20-%20Utilidades%20e%20integraciones/_INDICE-UTILIDADES.md) |
| Diseñar el juego: mecánicas, niveles, arte, UI, sonido, historia, producción | [13 · Diseño y producción](./13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/_INDICE-DISENO.md) |
| Aprender en español, en vídeo | [10 · Cursos en español](./10%20-%20Cursos%20en%20español/_INDICE-CURSOS-ES.md) |
| Saber qué cambió en 2026 | [02 · Novedades 2026](./02%20-%20Novedades%202026/) |
| Orientarme del todo | [`_indice/COMO-BUSCAR.md`](./_indice/COMO-BUSCAR.md) |

---

## Las cinco reglas que valen en todos los niveles

1. **Termina cosas pequeñas.** Diez juegos terminados enseñan más que un proyecto de tres años abandonado.
2. **Verifica antes de copiar.** Mucho código de internet es de GMS 1.x y usa funciones que ya no existen: `python3 "_indice/buscar.py" <función>`.
3. **Git desde el primer día**, antes de que el proyecto valga algo.
4. **Mide antes de optimizar.** El corpus real demuestra que las intuiciones sobre rendimiento suelen fallar.
5. **El manual manda.** Si un tutorial contradice a `09 - Manual oficial`, gana el manual.
