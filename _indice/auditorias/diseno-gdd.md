# Auditoría · Diseño de videojuegos como disciplina y el GDD

> **Dominio auditado:** el oficio de diseñar (no de programar): documento de diseño y sus
> variantes, teoría del diseño, diseño de sistemas y economía, progresión, balance, dificultad,
> puzzles, mundo y exploración, prototipado y playtesting, géneros y sus convenciones, game jam,
> ética, monetización y F2P, retención y analítica, pitch y comunicación del diseño.
>
> **Biblioteca auditada:** `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
> (GameMaker LTS 2026.0 · runtime `2026.0.0.23`). Se contaron como existentes la carpeta
> `13 - Diseño y producción de videojuegos` (14 documentos) y las recetas 28-31 de `04`.
> Se ignoraron `Lumbre/` y `GameMaker_Fuentes/`.
>
> **Fecha:** 6 de septiembre de 2026.

---

## 0 · Veredicto en tres frases

La carpeta `13` es **excelente en el núcleo del diseño de juego**: MDA, bucles anidados, flow,
curvas de dificultad, DDA y asistencia, economía con el vocabulario de Adams y Dormans, balance
por fórmulas con TTK, onboarding, prototipado, playtesting y GDD ligero están cubiertos con
código verificado, tablas numéricas reales y fuentes primarias con fecha. **Diseño de niveles
(13/02) y diseño narrativo (13/12) están, en mi opinión, por encima de lo que ofrece casi
cualquier material en español**: 13/02 aplica Kishōtenketsu, los diez principios de Dan Taylor,
métricas del jugador medidas en código y hoja de nivel; 13/12 cubre desde ludonarrativa hasta un
gestor de misiones con estado «fallada» y la aritmética de cuánto texto cabe en una caja.

Lo que falta no es «más de lo mismo», sino **tres bloques enteros y bien delimitados**:
(a) el **canon teórico más allá de MDA y Flow** — Koster, Salen & Zimmerman, Bartle/Quantic
Foundry, la teoría de la autodeterminación, las lentes de Schell, la incertidumbre de Costikyan;
(b) el **diseño de negocio y de servicio** — monetización y F2P, monedas múltiples, retención y
live ops, KPIs, y su cara ética (patrones oscuros, cajas de botín, juego responsable), del que la
biblioteca solo tiene la *implementación* técnica en `04/20`; (c) tres **especialidades de
diseño** con método propio que hoy no tienen documento: **puzzles**, **árboles de habilidades y
meta-progresión** y **simulación de balance (Monte Carlo)**.

En géneros, `04` cubre 15 con implementación completa, pero **el brief acierta**: faltan
idle/incremental, deckbuilder, táctica por turnos, horror, sigilo, granja/cozy, autobattler,
bullet heaven, party/minijuegos, educativos y palabras/trivia. Ritmo (04/19), gestión/tycoon
(04/13) y roguelite (04/05) **sí** están, contra lo que el brief sospechaba.

---

## 1 · Tabla completa

Leyenda: **C** = cubierto · **P** = parcial · **F** = falta.

### A · El documento de diseño

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| A1 | **GDD clásico completo** (concepto, pilares, público, plataformas, core loop, mecánicas, sistemas, progresión, economía, niveles, mundo, personajes, arte, audio, UI, técnica, monetización, marketing, calendario) | **F** | — (la biblioteca toma la postura contraria en `13/01 §8`: «Un GDD de 60 páginas se escribe una vez y no lo lee nadie») | Toda la plantilla larga y, sobre todo, **el criterio de cuándo sí hace falta**: equipo de más de uno, publisher, financiación pública, o un LLM que va a implementar veinte sistemas y necesita la especificación completa | Tim Ryan, «The Anatomy of a Design Document» I y II, *Game Developer* (19-10-1999) — verificado vivo hoy, HTTP 200; Tracy Fullerton, *Game Design Workshop*, cap. de documentación; plantillas de gamedesigning.org (200 OK) |
| A2 | **GDD de una página** | **C** | `13/01 §8.1 · GDD de una página — plantilla` | — (incluye pitch, estéticas MDA, verbos, los tres bucles, recorte explícito, riesgo nº 1 y métrica de éxito) | Stone Librande, «One-Page Designs», GDC 2010 |
| A3 | **Design pillars** (pilares de diseño) | **F** | — (0 apariciones de «pilar de diseño» / «design pillar») | El artefacto entero: 3-5 pilares en frase afirmativa, cómo se derivan de la experiencia buscada, y cómo se usan para **resolver una discusión de diseño**. Lo más cercano son las «dos estéticas objetivo (MDA), en orden» de `13/01 §1.3`, que cumplen una función parecida pero no son lo mismo | Schell, lente nº 1 (Experiencia Esencial); práctica estándar documentada en charlas GDC de pre-producción |
| A4 | **Ficha por sistema** | **C** | `13/01 §8.2 · Ficha por sistema — plantilla` | — (entradas, salidas, estado, reglas numeradas, tabla de parámetros de balance con «dónde vive», casos borde, telemetría) | Práctica estándar; equivalente al «system design doc» |
| A5 | **Wiki viva frente a documento estático** | **P** | `13/01 §8` (declara «dos artefactos cortos y vivos»); `13/11 §3.5 Registro de decisiones (ADR ligero)` y `§3.6 El diario de desarrollo` | Cómo se monta y se mantiene: repo/Obsidian/Notion, quién gana cuando el código y el documento discrepan, versionado del diseño junto al código, «diseño como código», y la regla de caducidad de una página | Fullerton, *Game Design Workshop*; práctica de estudio |
| A6 | **Pitch y elevator pitch** | **P** | `13/01 §8.1` casilla «Pitch (una frase, sin adjetivos)»; `13/11 §8.4 Press kit` (Descripciones, Características) | Cómo se **construye**: fórmula del gancho, «X con Y», qué NO va en el pitch, la diferencia entre pitch de venta (publisher, prensa, tienda) y pitch de diseño (para el equipo), y el pitch deck | Fullerton, cap. «Pitching»; Chris Zukowski, *How To Market A Game* (ya citado en `13/11 §6.1`) |
| A7 | **Comunicación del diseño: diagramas y flujos** | **P** | `13/05 §2.1 El mapa de pantallas`; `13/01 §2.2` (diagramas ASCII del bucle); `13/12 §8.4 Mapa de ramas`; `13/02 §4 La hoja de nivel` | Un catálogo de los diagramas de diseño y cuándo usar cada uno: diagrama de economía, grafo de gating/dependencias, mapa de progresión, diagrama de estados del jugador, tabla de interacción entre sistemas | Adams & Dormans (diagramas de economía); práctica GDC |
| A8 | **Público objetivo, personas y plataformas** | **P** | `13/01 §8.1` pide «Plataforma · duración de partida · público» en una línea; `13/11 §6.1` (decidir género y mantenerse en él) | El método: cómo se acota un público sin inventárselo, qué cambia en el diseño según plataforma (sesión corta en móvil, mando en consola, ratón en PC), y el análisis de la competencia como entrada de diseño, no de marketing | Fullerton; Zukowski, «pick your genre and stay in it» |

### B · Teoría

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| B1 | **MDA** | **C** | `13/01 §1.3 MDA: mecánica → dinámica → estética` y `§1.4 Usar MDA para diagnosticar un prototipo` | — (las tres capas con las definiciones del paper, las 8 «kinds of fun», y una tabla de diagnóstico síntoma → dinámica → mecánica → palanca que es lo mejor del documento) | Hunicke, LeBlanc y Zubek, *MDA* (2004) — PDF verificado vivo, HTTP 200 |
| B2 | **Lentes de Schell** | **P** | `13/01 §3.1` (solo la **lente del Flow**); Fuentes menciona Experiencia Esencial y Tétrada Elemental sin desarrollarlas | La Tétrada Elemental (mecánica/historia/estética/tecnología) como herramienta de encuadre, y un subconjunto operativo de 15-20 lentes usable como lista de revisión de diseño. La propia nota de `13/01` admite que no se pudo verificar la 3.ª edición | Jesse Schell, *The Art of Game Design: A Book of Lenses* |
| B3 | **Sylvester, *Designing Games*** | **P** | `13/01 §1.6 Diseño elegante` (elegancia, los tres «olores», emergencia) | El resto del libro: el juego como **motor de eventos emocionales**, ficción y mundo, el «flujo de emoción» de una sesión, y el criterio de decisión que propone frente al criterio de «características» | Tynan Sylvester, *Designing Games*, O'Reilly, 2013 |
| B4 | **Koster, *Theory of Fun*** | **F** | — (0 apariciones de «Koster» ni «Theory of Fun» en toda la biblioteca) | El marco entero: la diversión **es** el aprendizaje de un patrón, el aburrimiento como patrón agotado, «grokking», ruido frente a patrón, y por qué un juego «se acaba» cuando el jugador lo resuelve mentalmente. `13/01 §1.2` (bucle de Daniel Cook) cubre la idea nuclear pero no la fuente ni sus corolarios | Raph Koster, *A Theory of Fun for Game Design*, 2.ª ed. |
| B5 | **Salen & Zimmerman, *Rules of Play*** | **F** | — (0 apariciones) | El «círculo mágico», el juego como **sistema** (objetos, atributos, relaciones internas, entorno), los tres esquemas (reglas / juego / cultura), tipos de interactividad y, sobre todo, **«meaningful play»**, que es el término canónico del que cuelga todo el B8 | Katie Salen y Eric Zimmerman, *Rules of Play*, MIT Press, 2003 |
| B6 | **Flow** | **C** | `13/01 §3.1 Flow: la banda entre el aburrimiento y la ansiedad` | — (con el diagrama, las dos consecuencias operativas y la tesis de Jenova Chen citada literalmente) | Csikszentmihalyi; Jenova Chen, *Flow in Games* (USC, 2006) |
| B7 | **Motivación · teoría de la autodeterminación (autonomía / competencia / relación)** | **F** | — (0 apariciones de «autodeterminación», «autonomía», SDT) | El marco que explica **por qué** un sistema motiva, y sus consecuencias de diseño: la autonomía muere con el tutorial obligatorio y el objetivo único; la competencia exige feedback de progreso claro; la relación no es solo multijugador. Es el complemento natural a MDA y a Flow, que están | Ryan & Deci, SDT; Rigby & Ryan, *Glued to Games* (modelo PENS) |
| B8 | **Tipos de jugador (Bartle · Quantic Foundry)** | **F** | — (0 apariciones de ninguno de los dos) | Bartle (asesino/triunfador/explorador/socializador) con su advertencia de que nació para MUDs, y el modelo empírico moderno de Quantic Foundry (6 clusters / 12 motivaciones) como herramienta para decidir a quién se sirve y a quién no | Richard Bartle, *Hearts, Clubs, Diamonds, Spades* (mud.co.uk, HTTP 200 hoy); Quantic Foundry, Gamer Motivation Model (sitio vivo; devuelve 403 a herramientas automáticas) |
| B9 | **Decisiones significativas (*meaningful choices*)** | **P** | `13/01 §2.3` («una decisión es interesante cuando cada opción es la mejor en algún contexto»); `13/12 §4.6 Elecciones que importan frente a ilusión de elección` (lado narrativo) | El marco general y sus cuatro palancas: coste de oportunidad, información incompleta, irreversibilidad y consecuencia visible. La regla operativa está; el vocabulario y el método de auditar una decisión, no | Sid Meier, «a series of interesting decisions»; Salen & Zimmerman, *meaningful play* |
| B10 | **Riesgo y recompensa** | **C** | `13/02 §1.5 Riesgo, recompensa, secretos y atajos`; `13/01 §2.2` casillas [2] RIESGO y [3] RECOMPENSA del bucle | Muy sólido para niveles. Lo sistémico (apostar recursos, *push your luck*, la decisión de retirarse) queda implícito | Dan Taylor, «Ten Principles of Good Level Design», GDC 2013 (ya citado en `13/02 §1.7`) |
| B11 | **Incertidumbre** | **P** | `13/13 §5 Probabilidad y aleatoriedad` (distribuciones, bolsa aleatoria, aleatorio con memoria, crítico con piedad, histograma de comprobación) | La **taxonomía de diseño**, no la mecánica: incertidumbre de rendimiento, del solucionador, del oponente, narrativa; y sobre todo **azar de entrada frente a azar de salida** (`input` vs `output randomness`), que es la decisión que más define un juego de estrategia o de cartas | Greg Costikyan, *Uncertainty in Games*, MIT Press, 2013 |
| B12 | **Bucles de realimentación positivos y negativos** | **C** | `13/01 §4.2 Realimentación: por qué las partidas se deciden pronto o no acaban nunca` | — (tabla con efecto, ejemplo clásico y herramienta concreta; la receta de «acotar la positiva, no eliminarla») | MDA (2004), ejemplos del termostato y Monopoly |
| B13 | **Dominancia estratégica** | **P** | `13/01 §1.4` (fila «Todos eligen lo mismo» de la tabla de diagnóstico); `13/01 §2.3` («si una opción gana siempre, bórrala») | El vocabulario y el método: estrategia dominante y dominancia débil, estrategias degeneradas, «el óptimo aburrido», cómo se caza —telemetría de tasa de uso por opción, simulación, playtest dirigido— y cómo se arregla sin nerfear a ciegas | Teoría de juegos aplicada; charlas GDC de balance de juegos competitivos |
| B14 | **Emergencia** | **P** | `13/01 §1.6` (definición de Sylvester + matriz fuego/agua/electricidad/viento) | La distinción canónica **emergencia frente a progresión** (Juul) y el diseño deliberado para emergencia: reglas ortogonales, sistemas que se hablan entre sí, verbos que aplican a todo, y el coste de QA que eso implica | Jesper Juul, *Half-Real* (emergence vs progression); Sylvester |

### C · Diseño de sistemas y economía

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| C1 | **Mecánicas frente a sistemas** | **C** | `13/01 §1.5 Mecánicas frente a sistemas` (+ «la regla del segundo sistema») | — | Sylvester; Adams & Dormans |
| C2 | **Economía interna: fuentes, sumideros, convertidores, intercambiadores** | **C** | `13/01 §4.1 El vocabulario correcto` (con el aviso convertidor ≠ intercambiador) | — (vocabulario correcto del libro de referencia, traducido y con ejemplos) | Adams y Dormans, *Game Mechanics: Advanced Game Design*, 2012 |
| C3 | **Machinations** | **P** | Citada solo como origen del libro en `13/01 · Fuentes` (enlace a machinations.io) | La **notación** y el método: pool, source, drain, gate, converter, conexiones de recurso y de estado; cómo se dibuja la economía antes de programarla y cómo se simula ahí; y qué se traduce después a `balance.json`. La biblioteca ya trata economía, así que la herramienta estándar para diagramarla es un hueco real | Adams & Dormans, cap. 5-6; machinations.io (HTTP 200 hoy) |
| C4 | **Inflación** | **C** | `13/01 §4.3 La regla que evita el 80 % de los desastres de economía` | — (incluye método de detección: oro por minuto, tres formas de curva y su diagnóstico) | Adams & Dormans |
| C5 | **Monedas múltiples (blanda / dura / premium)** | **F** | — (0 apariciones útiles de «moneda blanda», «divisa», «premium») | El patrón: por qué existen dos o tres monedas, qué separa cada una, tipos de cambio y por qué nunca son bidireccionales, la moneda de meta-progresión frente a la de partida. `04/05` **usa** dos monedas (oro de partida y desbloqueos permanentes) sin nombrar ni explicar el patrón | Adams & Dormans; literatura de diseño F2P |

### D · Progresión

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| D1 | **XP y niveles** | **C** | `04/04 §5.1 Niveles y curva de experiencia` (constructor `Progression` completo); `13/13 §8.4 Invertir la curva: nivel a partir de la XP acumulada` | — | Práctica estándar |
| D2 | **Power curves** | **C** | `13/13 §8.1 Las cinco formas`, `§8.2 Las cinco curvas a diez niveles`, `§8.3 Cuál para qué`; `13/01 §4.4 Balance por fórmulas, con números` (coste geométrico, TTK, balancear en múltiplos) | — Es de lo mejor de la biblioteca: cinco curvas con código, tabla numérica calculada y criterio de aplicación por sistema | Práctica estándar |
| D3 | **Árboles de habilidades** | **F** | Dos menciones de una línea: `04/06 §8 Cómo escalarlo` punto 3, y `13/05 §1.1` como ejemplo de pantalla | Todo: topologías (lineal, ramas, malla, esfera, tablero), el criterio de diseño (nodo que **cambia cómo juegas** frente a nodo «+5 % de daño»), prerrequisitos y respec, modelo de datos en GML y la UI navegable con mando | Práctica estándar; charlas GDC de sistemas de progresión |
| D4 | **Desbloqueos y meta-progresión** | **P** | `04/05 §4.7 Muerte permanente y meta-progresión` y `§5.8 Run state y meta-progresión` (código de `MetaProgress`); `13/06` (perfil persistente frente a partida) | El **diseño**, no la implementación: cuánta meta-progresión antes de que el juego se gane solo, meta-progresión de **poder** frente a de **opciones**, su efecto sobre la curva de dificultad, y qué hacer con el jugador que ya lo desbloqueó todo | Debate documentado alrededor de Hades / Dead Cells / Returnal en GDC y prensa especializada |
| D5 | **Gating** | **C** | `13/01 §5.3 Gating: la mecánica no aparece hasta que la anterior está probada` (con código `contenido_permitido`); `13/02 §1.4 Gating: llaves, cerraduras y puertas blandas` | — | Práctica estándar; Dan Taylor |

### E · Balance

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| E1 | **Hojas de cálculo y fórmulas** | **C** | `13/01 §4.4` y `§4.5 De la hoja de cálculo al juego` (pipeline hoja → CSV/JSON → struct, con cinco reglas); `13/01 §9.3 Datos de balance en Included Files` | — | Práctica estándar |
| E2 | **Simulación (Monte Carlo)** | **F** | Solo dos menciones de pasada: `13/01 §2.3` («simular 100 iteraciones de la economía en columnas») y `13/02 §2` («la simulación da el número con el que se construye») | El método y el código: simular 10 000 combates o 10 000 partidas de economía, leer la **distribución** y no la media, percentiles, y usarlo para cazar dominancia y varianza excesiva antes de gastar un playtest. Encaja de forma natural con el `scr_pruebas` de `13/10 §3` | Adams & Dormans (simulación en Machinations); charlas GDC de balance cuantitativo |
| E3 | **Playtesting cuantitativo** | **C** | `13/01 §3.4 Medir la dificultad con datos, no con opiniones` (4 métricas, mediana no media) y `§9.5 Telemetría` (código completo con volcado a JSON); `13/10 §10.2 Qué medir` y `§10.4 Telemetría mínima` | — | Valve (instrumentación de *Half-Life*); Games User Research |
| E4 | **Tuning knobs** | **C** | `13/01 §8.3 Qué se fija antes de programar y qué se decide jugando`; `§9.2 scr_config`, `§9.3 balance.json`, `§9.4 Balance en caliente con el Debug Overlay` | — Está el concepto entero (aunque no el anglicismo) y, además, implementado: panel `dbg_*` que ajusta sin recompilar y `balance_restaurar()` | Práctica estándar |

### F · Dificultad

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| F1 | **Curvas de dificultad** | **C** | `13/01 §3.2 Las cuatro formas de curva` (rampa, dientes de sierra, escalones, pico y valle + regla del 3+1) | — | Chen, *Flow in Games*; práctica estándar |
| F2 | **Modos de dificultad** | **P** | `13/01 §3.3` (recomienda asistencia granular **frente a** «Fácil/Normal/Difícil»); `04/25 Menú de opciones y ajustes` (el widget) | Cómo se construye un modo sin duplicar contenido: qué multiplicadores se tocan (daño recibido, densidad, i-frames) y cuáles no, cómo se prueba cada modo sin triplicar el QA, y qué hacer con logros y finales | Práctica estándar; documentación de accesibilidad de plataformas |
| F3 | **Dificultad dinámica (DDA)** | **C** | `13/01 §3.3 Dificultad dinámica: las dos familias, y cuál elegir` | — (incluye la lista de qué se puede ajustar en silencio y qué no, con el razonamiento) | Chen (2006) |
| F4 | **Assist mode · «la dificultad es un problema de UX»** | **C** | `13/01 §3.3` (caso *Celeste* con cita literal de Maddy Thorson y el detalle del renombrado desde «Cheat Mode»); `04/27 Accesibilidad` | — | Declaraciones públicas de Maddy Thorson; guías de accesibilidad en videojuegos |

### G · Especialidades de diseño

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| G1 | **Diseño de puzzles** | **F** | `04/07 Puzzle y Match-3` es una receta de **implementación** de tablero (detección de matches, cascadas, gravedad, shuffle): no enseña a diseñar un puzzle | Todo el oficio: taxonomía (lógica, física, Sokoban/empuje, secuencia, observación, léxico), el momento **«ajá»** y cómo se protege, enseñar la regla del puzzle sin enunciarla, medir la dificultad de un puzzle (pasos frente a profundidad de la idea), pistas falsas, soluciones no deseadas, y generación y **validación por búsqueda** (BFS/A* sobre estados) — que enlazaría con `13/07` | Charlas GDC de Jonathan Blow (*Braid*, *The Witness*) y de Alan Hazelden; Bob Bates, *Game Design*, cap. de puzzles |
| G2 | **Diseño de mundo y exploración** | **P** | `13/02 §2.6 Tipos de estructura` (lineal, hub, mundo abierto por zonas, metroidvania, procedural, con coste y receta); `13/02 §1.3 Legibilidad: puntos de referencia, weenies y líneas de guía`; `04/06 Metroidvania` (implementación) | Densidad y distribución de **puntos de interés**, el bucle curiosidad → observación → navegación → recompensa, mapa y brújula **como decisión de diseño** (y el coste de llenar el mapa de iconos), viaje rápido y lo que destruye, y el **grafo de bloqueos** de un metroidvania como artefacto que se dibuja antes de construir salas | Christopher Totten, *Architectural Approach to Level Design* (ya citado en `13/02`); charlas GDC de mundo abierto |
| G3 | **Diseño de niveles** | **C** | `13/02` completo — juzgado: **sobresaliente**. `§1.1` (introducir/desarrollar/torcer/concluir), `§1.7` los diez principios de Dan Taylor, `§2.1 Las métricas del jugador`, `§3.11 Medir las métricas de salto en código`, `§4 La hoja de nivel` | — Nada relevante de mi dominio | Dan Taylor, GDC 2013; Totten |
| G4 | **Diseño narrativo** | **C** | `13/12` completo — juzgado: **sobresaliente** (2 073 líneas). `§1.4 Ludonarrativa`, `§2.6 Las formas de la narrativa interactiva (y su coste)`, `§3.5 Barks`, `§4.5 Cuánto texto cabe en una caja`, `§4.7 Ramificar cuesta; converger es la solución`, `§6.5 Gestor de misiones`, `§8 Plantillas` | — Nada relevante de mi dominio | Referencias del propio documento |
| G5 | **Onboarding** | **C** | `13/01 §5 Onboarding: enseñar sin texto` (una idea nueva cada vez, las cinco herramientas, gating con código, el examen de los primeros 60 segundos) | Menor: la métrica de retención de los primeros minutos (FTUE) y el tutorial explícito cuando el juego lo exige (estrategia, gestión) | Lectura crítica de *Super Mario Bros.* 1-1, citada con su advertencia en el propio texto |
| G6 | **Prototipado y prototipo de papel** | **P** | `13/01 §6 Prototipado rápido` (qué se prototipa, cajas grises, cuándo tirarlo, escribir la pregunta en la primera línea); `§2.3 Probarlo sin motor` (la «prueba de papel» en una fila de tabla) | Cómo se monta un prototipo de papel de verdad: componentes, cómo se juega un turno, qué géneros lo permiten y cuáles no, y qué se aprende y qué **no** se puede aprender así (nada de game feel) | Fullerton, *Game Design Workshop* (el libro está construido alrededor del prototipado físico) |
| G7 | **Playtesting** | **C** | `13/01 §7 Playtesting` (postura, qué preguntar y qué no, cinco por ronda, plantilla de registro de 4 columnas); `13/10 §10 Playtesting` (protocolo, qué medir, observación → diagnóstico → tarea con criterio de aceptación) | — Uno de los tratamientos más completos que he visto en español | Valve sobre *Half-Life* (200 sesiones); Nielsen (con la advertencia de extrapolación explícita en el texto); Games User Research |

### H · Géneros y sus convenciones

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| H1 | Plataformas · top-down · shmup · RPG · roguelike/roguelite · metroidvania · match-3 · tower defense · survival · VN · arcade · carreras · estrategia y gestión · multijugador · ritmo | **C** | `04/01`…`04/19`, cada una con `§1 Visión general` (definición del género, subgéneros y referencias) + implementación completa | — Ritmo (`04/19`), gestión/tycoon (`04/13 §1`) y roguelite (`04/05`) **sí están**, contra lo que sugería el brief | `04/_INDICE-RECETAS.md` |
| H2 | **Bullet heaven** (Vampire Survivors) | **P** | Una fila de tabla en `04/09 §1` («*Bullet heaven*: oleadas automáticas, builds») + `07/06` menciona la plantilla oficial *Survivor* | El género que más se hace hoy: ataque automático, construcción de build por oleada, escalado de miles de enemigos, curva de sesión de 20-30 min. `04/09` es survival de necesidades, que es otra cosa | Plantilla oficial *Survivor* del IDE; análisis del género en GDC |
| H3 | **Autobattler** | **P** | Una fila de tabla en `04/13 §1` | Igual que H2: economía de rondas, emparejamiento, sinergias, la tienda con reroll | — |
| H4 | **Idle / incremental / clicker** | **F** | 0 (solo `03/_DESCUBIERTAS.md` cita una serie de YouTube de *Cow Clicker*) | Prestigio, números grandes, progreso sin conexión, la curva exponencial ya está en `13/13 §8` pero no el género que la usa como núcleo | Análisis canónico del género (Cookie Clicker, Adventure Capitalist) |
| H5 | **Deckbuilder** | **F** | 0 | Mazo/mano/descarte/exilio, curva de mazo, «adelgazar el mazo» como decisión, sinergias | *Slay the Spire* está citado como ejemplo de bucle en `13/01 §2.2` pero no como género |
| H6 | **Táctica por turnos** | **F** | Una fila en `04/04 §1` («Táctico por turnos, grid, Final Fantasy Tactics») | Rejilla táctica, orden de turno, línea de visión y cobertura, IA táctica, porcentajes de acierto y su percepción | — |
| H7 | **Horror** | **F** | 0 | Recursos escasos, telegrafiado del peligro, ritmo de tensión, el enemigo que no se puede matar, sonido como mecánica | — |
| H8 | **Sigilo** | **F** | Una fila en `04/02 §1` («Táctico / sigilo, Hotline Miami») | Conos de visión y estados de alerta legibles, la regla del «segundo intento», el fallo que no acaba la partida. El **material técnico existe** (`13/13 §2.4 Cono de visión`, `04/31 §percepción`), pero no el diseño | — |
| H9 | **Granja / pesca / cozy (Stardew-like)** | **F** | Una fila en `04/09 §1` («Farming sim: supervivencia sin amenaza») | El género completo: calendario y estaciones, relaciones con NPC, ausencia de fracaso, economía de temporada, ritmo tranquilo como diseño deliberado | — |
| H10 | **Party games, minijuegos, educativos, palabras y trivia, extraction** | **F** | 0 | Todos. Son los géneros más habituales en encargos pequeños (educativo, trivia) y, en el caso de los minijuegos, aparecen dentro de otros géneros sin guía propia | — |
| H11 | **Convenciones de género como capítulo de diseño** | **F** | No existe un documento que reúna «qué espera el jugador de cada género y qué pasa si lo rompes». Está repartido en el `§1 Visión general` de cada receta | Un cuadro transversal: qué convención es esperada (guardado, mapa, dificultad, duración de sesión, controles), cuál se puede romper y cuál se rompe a tu costa | Práctica de análisis de género |

### I · Contexto, negocio y ética

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| I1 | **Alcance (*scope*)** | **C** | `13/11 §1 Alcance: el único problema que de verdad mata juegos` (estimar ×3, `§1.4` prototipo/MVP/vertical slice, `§1.5` matriz de recorte, `§1.6` feature creep) | — Excelente, con la definición canónica de vertical slice de Greg Donovan | Donovan (Volition), *The Vertical Slice* |
| I2 | **Game jam como método** | **P** | `07/08 §3 Game jams relevantes` (catálogo: GMTK, Micro Jam); `05/02` (HTML5 como formato de jam); `07/11` cita el caso «From Game Jam to 600k Sales» | El **método**: qué se recorta en 48 h, cómo se interpreta el tema, la plantilla pre-jam permitida, el reparto de horas, y sobre todo **qué se hace con el prototipo después** — el paso de jam a proyecto, que la biblioteca cita como caso de éxito pero no explica | GMTK Game Jam; caso *The King Is Watching* en el blog oficial de GameMaker |
| I3 | **Ética: patrones oscuros, cajas de botín, juego responsable** | **F** | 0 apariciones. `13/05 · Fuentes` reconoce que **no pudo verificar** la fuente sobre *dark patterns* | El catálogo de patrones oscuros de diseño (rejilla de energía, cuenta atrás con FOMO, pay-to-skip, grindeo forzado, moneda ofuscada), las cajas de botín y su situación legal (Bélgica, Países Bajos, y el marco español), y el diseño de juego responsable (límites de sesión, transparencia de probabilidades) | Deterding et al. sobre dark patterns en juegos; regulación europea de cajas de botín |
| I4 | **Monetización y diseño F2P** | **F como diseño** (**C como implementación**) | Implementación: `04/20 Servicios de plataforma` (logros, leaderboards, AdMob, IAP por extensión, nube) y `04/28 §10 Monetización y servicios` (que remite a la anterior); precio y regiones en `13/11 §6.7 Fecha, precio y regiones` | El **diseño**: elegir modelo (premium, demo, F2P, DLC), qué se vende y qué no se vende nunca (cosmético frente a poder), diseño de la tienda y del anuncio recompensado, pase de temporada, y el efecto que cada modelo tiene sobre el resto del diseño. Hoy la biblioteca sabe **llamar a la API de IAP** pero no **qué poner dentro** | Literatura de diseño F2P; charlas GDC de monetización; regulación de tiendas ya citada en `04/28` |
| I5 | **Retención y live ops** | **F** | Lo más cercano: `13/11 §7 Post-lanzamiento` (parches, roadmap público sí/no, telemetría con consentimiento, postmortem) — que es el modelo indie premium, no un servicio | Temporadas y eventos, calendario de contenidos, el ciclo de una temporada, recompensas por conexión, reenganche, y la decisión de **no** hacer live ops (que para un indie suele ser la correcta, pero hay que argumentarla) | Prensa y charlas de live ops; el blog «Deconstructor of Fun» ya catalogado en `07/11` |
| I6 | **Analítica de diseño: KPIs y embudos** | **P** | `13/01 §3.4` (embudo de progreso, muertes por sala, tiempo mediano, intentos) y `§9.5-9.6` (telemetría con volcado y lectura); `13/10 §10.4` | Los KPIs de producto y negocio: retención D1/D7/D30, duración media de sesión, conversión, LTV; el embudo de tienda (impresión → página → lista de deseados → compra → reembolso) y qué de eso da Steamworks de verdad; y la regla de cuántos datos hacen falta para que un número signifique algo | Documentación de Steamworks (ya usada en `13/11 §6`); práctica de analítica de producto |

---

## 2 · Propuestas, priorizadas

### Prioridad alta

**1 · `13 - Diseño y producción de videojuegos/14 - El documento de diseño: del one-pager al GDD completo.md`**
Cierra A1, A3, A5, A6, A7, A8. Empieza donde `13/01 §8` lo deja: cuándo el one-pager **no basta**
y qué se escribe entonces. Plantilla completa por secciones (concepto y pitch, pilares, público y
plataformas, core loop, mecánicas, sistemas, progresión, economía, niveles, mundo y personajes,
arte, audio, UI, técnica, monetización, marketing, calendario), cada una con «qué va aquí, qué NO
va aquí y en qué documento de esta biblioteca está desarrollada». Añade pilares de diseño (3-5,
en frase afirmativa, con el ejemplo de resolver una discusión con ellos), elevator pitch, la wiki
viva frente al documento congelado, y el catálogo de diagramas de diseño. Cierra con la versión
**para LLM**: qué tiene que contener un GDD para que un agente pueda implementarlo sin inventarse
nada, que es el caso de uso propio de esta biblioteca.

**2 · `13/15 - Teoría del diseño: el canon en una tarde.md`**
Cierra B2, B4, B5, B7, B8, B9, B11, B13, B14. Un documento por marco, con la ficha operativa de
cada uno y, en cada apartado, «qué te hace hacer distinto mañana»: Koster (la diversión es
aprender un patrón), Salen & Zimmerman (círculo mágico, juego como sistema, *meaningful play*),
Schell (Tétrada Elemental y 15-20 lentes usables como lista de revisión), SDT (autonomía,
competencia, relación), Bartle y Quantic Foundry (con la advertencia de para qué sirve y para qué
no), Costikyan (taxonomía de incertidumbre y azar de entrada frente a azar de salida), dominancia
estratégica y estrategias degeneradas, y emergencia frente a progresión (Juul). Enlaza a `13/01`
en lugar de repetir MDA y Flow, que ya están bien.

**3 · `13/16 - Progresión: árboles de habilidades, desbloqueos y meta-progresión.md`**
Cierra D3 y D4, y absorbe C5. Topologías de árbol y qué comunica cada una; el criterio «un nodo
que cambia cómo juegas vale por diez nodos de +5 %»; prerrequisitos, respec y coste; modelo de
datos en GML (grafo como struct, validación de ciclos, guardado versionado) y la UI navegable con
mando apoyada en `13/05 §2.2`. Después, meta-progresión: cuánta antes de que el juego se gane
solo, poder frente a opciones, su efecto sobre la curva de `13/01 §3.2`, el jugador que ya lo
desbloqueó todo, y el patrón de **monedas múltiples** (partida frente a meta) que `04/05` ya usa
sin nombrar.

**4 · `13/17 - Diseño de puzzles.md`**
Cierra G1, el hueco más nítido: `04/07` es una implementación de match-3 y no cubre nada de esto.
Taxonomía (lógica, física, empuje/Sokoban, secuencia, observación, léxico), el momento «ajá» y
qué lo mata, enseñar la regla sin enunciarla (aplicando el `13/01 §5` a puzzles), medir la
dificultad de un puzzle, pistas falsas y soluciones no deseadas, y la parte de ingeniería:
representar el estado, **validar por búsqueda** (BFS/A*) que el puzzle tiene solución y que **no
tiene la solución tonta**, y generación con validación — que enlaza directo con `13/07`.

### Prioridad media

**5 · `13/18 - Modelo de negocio, monetización y ética del diseño.md`**
Cierra I3, I4, I5 e I6, que son cuatro huecos que se explican juntos y por separado quedarían en
cuatro documentos anémicos. Elegir modelo (premium, demo, F2P, DLC, suscripción) y su efecto en
el resto del diseño; qué se vende y qué no; el anuncio recompensado y el pase de temporada como
piezas de diseño, no de API; el catálogo de patrones oscuros con el porqué de cada uno; cajas de
botín y su situación legal en Europa; juego responsable; retención y live ops, incluyendo el
argumento de **no** hacerlas; y los KPIs con el embudo de tienda. Remite a `04/20` para la
implementación y a `13/11 §6-9` para precio, regiones y legal, que ya están.

**6 · `13/19 - Balance por simulación: Monte Carlo, Machinations y estrategias dominantes.md`**
Cierra E2, C3 y B13. La notación de Machinations para diagramar la economía antes de programarla,
y su traducción a `balance.json`. Después, la simulación en GML apoyada en el `scr_pruebas` de
`13/10 §3`: correr 10 000 combates o 10 000 partidas, leer distribución y percentiles en vez de
medias, y usarla para cazar dominancia (tasa de uso por opción, tasa de victoria por build) y
varianza excesiva. Es la continuación natural de `13/01 §4.4-4.5`, que da las fórmulas pero no
la forma de comprobarlas sin gastar playtests.

**7 · `04 - Recetas por género/32 - Bullet heaven, autobattler y deckbuilder.md`**
Cierra H2, H3 y H5: los tres géneros de moda que hoy solo tienen una fila de tabla. Un documento
con tres bloques, porque comparten esqueleto (bucle de rondas u oleadas, construcción de build,
economía de mejora, escalado numérico). Incluye la plantilla oficial *Survivor* del IDE como punto
de partida y el problema real de rendimiento con miles de entidades, que ya tiene material en
`04/03` (object pooling) y `01/15`.

### Prioridad baja

**8 · `13/20 - Diseño de mundo y exploración.md`** — cierra G2. Densidad y distribución de puntos
de interés, el bucle curiosidad → observación → navegación → recompensa, mapa y brújula como
decisión (y el coste de llenar el mapa de iconos), viaje rápido, y el grafo de bloqueos de un
metroidvania como artefacto que se dibuja antes de construir salas. Puede entrar como sección
`§2.7` de `13/02`, que ya tiene `§2.6 Tipos de estructura`, si se prefiere no crear documento.

**9 · Ampliar `13/01` con dos secciones cortas** — cierra F2 y G6 sin documento nuevo:
`§3.5 Modos de dificultad sin duplicar contenido` (qué multiplicadores tocar y cuáles no, coste de
QA, logros y finales) y `§6.4 El prototipo de papel, en concreto` (componentes, cómo se juega un
turno, qué géneros lo permiten, y qué no se puede aprender así).

**10 · `04/33 - Géneros sin receta: sigilo, horror, táctica por turnos, granja y cozy, idle.md`**
Cierra H4, H6, H7, H8, H9. No una receta completa por género —serían cinco documentos— sino, por
cada uno, sus convenciones, sus tres sistemas críticos y a qué receta y a qué documento de `13`
apoyarse. En sigilo, en particular, el material técnico ya existe (`13/13 §2.4 Cono de visión`,
`04/31` percepción con vista/oído/memoria): lo que falta es el diseño.

**11 · `13/21 - Game jam: método y qué hacer con lo que sale.md`** — cierra I2. Qué se recorta en
48 h, cómo se interpreta el tema, la plantilla pre-jam permitida, el reparto de horas, y el paso
de jam a proyecto que la biblioteca cita como caso de éxito (*The King Is Watching*) pero no
explica. Alternativa más barata: una sección `§12` en `13/11`, que ya trata alcance y fases.

**12 · Un cuadro transversal de convenciones de género** — cierra H11 y H10. Una tabla en
`04/_INDICE-RECETAS.md` o en `13/01`: qué espera el jugador de cada género (guardado, mapa,
duración de sesión, dificultad, controles), cuál de esas convenciones se puede romper y cuál se
rompe a tu costa. Recoge de paso los géneros pequeños (party, minijuegos, educativos, trivia,
extraction) sin necesidad de receta propia.

---

## 3 · Limitaciones de esta auditoría

- **El presupuesto de `WebSearch` de la sesión estaba agotado** (200/200 consumidas antes de que
  yo empezara). Verifiqué las fuentes externas con `curl -A "Mozilla/5.0"` comprobando código de
  respuesta y, donde pude, contenido: **200 OK** en `machinations.io`, `mud.co.uk/richard/hcds.htm`
  (Bartle), `gamedesigning.org/learn/game-design-document/`, `gamedocs.org`, `gdcvault.com`, el PDF
  de MDA en Northwestern y el artículo de Tim Ryan en `gamedeveloper.com` (del que confirmé que
  menciona *target audience*, *game mechanics*, *game elements*, *artificial intelligence* e
  *interface*). Devolvieron **403/406** a herramientas automáticas —lo que significa bloqueo de
  bot, no que el sitio esté caído— `quanticfoundry.com`, `theoryoffun.com` y
  `selfdeterminationtheory.org`. **De `gamedesigning.org` no pude extraer la lista de secciones de
  su plantilla**: la página carga el contenido por JavaScript y el HTML crudo solo trae estilos.
  Las atribuciones a Koster, Salen & Zimmerman, Schell, Sylvester, Costikyan, Fullerton, Bartle y
  Juul proceden de mi conocimiento del canon, **no de una lectura de la fuente hoy**.
- **No abrí los 3 033 documentos del manual español** (`09 - Manual oficial/`). Es referencia de
  API y no cubre diseño de juego, así que lo di por irrelevante para este dominio; si algún tema
  estuviera ahí, se me habría escapado.
- **De `11 - Código descargado` solo consulté el catálogo indirectamente**, vía `buscar.py`. Es
  posible que alguna librería de terceros implemente un árbol de habilidades o una economía y que
  eso reduzca el coste de las propuestas 3 y 6, pero no cambiaría el diagnóstico: falta la
  **documentación de diseño**, no el código.
- **Leí completos** `13/01` (el documento central de mi dominio) y las secciones relevantes de
  `13/02`, `13/05`, `13/10`, `13/11`, `13/12`, `13/13 §8` y `§5`, `04/07`, `04/09 §1`, `04/13 §1`,
  `04/04 §5.1`, `04/06 §8`, `04/20` y `04/28 §10`. De los demás documentos de `13` y `04` revisé
  encabezados y resultados de búsqueda, no el texto entero.
- **La calificación de «sobresaliente» de `13/02` y `13/12` es un juicio**, pedido por el brief, y
  se basa en su estructura, en la densidad de fuentes primarias con fecha y en que aplican teoría
  real (Kishōtenketsu, Taylor, Totten, ludonarrativa) a código verificado — no en una comparación
  sistemática con otros materiales.
- **No escribí ni modifiqué nada** dentro de la biblioteca. Este informe vive fuera de ella.
