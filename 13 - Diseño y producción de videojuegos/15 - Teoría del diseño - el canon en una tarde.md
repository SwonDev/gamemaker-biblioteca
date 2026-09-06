# 15 · Teoría del diseño — el canon en una tarde

> Nueve marcos que cualquier diseñador con formación acaba citando, cada uno reducido a **una
> ficha operativa** y a una lista de **qué te hace hacer distinto mañana**. No es teoría por la
> teoría: cada marco trae una pregunta de diagnóstico que puedes hacerte hoy mismo sobre tu
> proyecto, y sirve para algo distinto — por eso el documento cierra con una tabla de «qué marco
> usar para qué problema» en vez de pedirte que los memorices todos.
>
> **Qué NO cubre.** MDA y Flow —los dos marcos que más se citan de todos— ya están completos en
> [13 · 01 §1.3-1.4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#13--mda-mecánica--dinámica--estética)
> y [§3.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#31--flow-la-banda-entre-el-aburrimiento-y-la-ansiedad):
> no se repiten aquí, solo se cruzan con los marcos nuevos cuando aporta algo. La regla operativa
> de las **decisiones significativas** ya está en
> [13 · 01 §2.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#23--probarlo-sin-motor)
> («una decisión es interesante cuando cada opción es la mejor en algún contexto»); este
> documento la sitúa dentro del marco más amplio de Salen & Zimmerman en vez de repetirla. La
> **dominancia estratégica aplicada a un caso de GameMaker** (tabla de daño, TTK) ya tiene su
> vocabulario en [13 · 01 §1.4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#14--usar-mda-para-diagnosticar-un-prototipo)
> y [§4.4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números);
> aquí se le da el marco teórico y el método de caza que allí faltaba. El **documento de diseño y
> sus plantillas** están en
> [13 · 14](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md).
> El **árbol de habilidades y la meta-progresión** —que usan varios de estos marcos, sobre todo
> SDT y dominancia— están en
> [13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades%2C%20desbloqueos%20y%20meta-progresión.md).
> El **modelo de negocio, la monetización, las cajas de botín y la ética del diseño** quedan fuera
> de esta biblioteca a fecha de hoy: es un hueco señalado en
> `_indice/auditorias/diseno-gdd.md` y no se rellena aquí para no fingir una cobertura que no
> existe. La **simulación de balance por Monte Carlo** y la notación de **Machinations** tampoco
> están todavía: la dominancia de §8 se caza aquí con telemetría, no con simulación masiva.

---

## 1 · Cómo leer este documento

No lo leas de un tirón. Cada uno de los nueve apartados siguientes tiene la misma forma:

1. **El marco**, en cuatro o cinco párrafos: la idea central, de dónde sale y qué la hace
   distinta de las demás.
2. **Ficha operativa**, una tabla de cinco filas: qué explica, la pregunta de diagnóstico que
   puedes hacerte hoy, cuándo se aplica, cuándo NO sirve, y un ejemplo real y verificado.
3. **Qué te hace hacer distinto mañana**: una lista de 4-6 decisiones concretas de diseño que
   cambian si te tomas el marco en serio. Esta es la parte que se queda; el resto es contexto.

La primera vez, lee solo las nueve fichas operativas y la lista de «qué usar para qué problema»
del [§12](#12--tabla-qué-marco-usar-para-qué-problema). Vuelve al «marco» completo de un apartado
solo cuando la ficha no te baste, o cuando necesites citarlo bien delante de alguien. Los nueve
marcos no compiten entre sí — cada uno ilumina una parte distinta del mismo sistema, como MDA
(mecánica/dinámica/estética) y Flow (reto/habilidad) ya hacían antes de este documento.

---

## 2 · Koster — la diversión es aprender un patrón

### 2.1 · El marco

Raph Koster publicó *A Theory of Fun for Game Design* en 2004 (2.ª edición, Paraglyph Press /
O'Reilly, 2013). Su tesis central, resumida sin adornos: **la diversión es la retroalimentación
que da el cerebro cuando reconoce y domina un patrón nuevo.** Un juego es, en este marco, un
espacio de práctica seguro donde el cerebro entrena el circuito de reconocimiento de patrones que
usa para todo lo demás — desde esquivar un depredador hasta anticipar el movimiento de un rival.

La consecuencia dura del marco es esta: **un juego deja de divertir en el momento exacto en que
el jugador termina de aprender su patrón**, no cuando el contenido se acaba. Koster llama
«*grokking*» al instante en que el patrón queda completamente interiorizado — a partir de ahí, la
misma actividad que antes generaba una descarga de dopamina se vuelve mecánica y aburrida, porque
ya no hay nada que aprender. El aburrimiento, en este marco, no es un fallo del juego: **es la
prueba de que el aprendizaje ha terminado.**

Esto conecta directamente con el bucle de aprendizaje de Daniel Cook que ya tienes en
[13 · 01 §1.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#12--el-bucle-de-aprendizaje-por-qué-el-jugador-vuelve)
(acción → simulación → feedback → modelo mental): Koster explica **por qué** ese cuarto paso
produce placer, no solo que hace falta que ocurra. Un juego con muchos sistemas que se cruzan
entre sí (§1.6 de ese mismo documento, la matriz fuego/agua/electricidad/viento) dura más
precisamente porque ofrece más patrones distintos que aprender, y los aprende uno detrás de otro
en vez de todos a la vez.

> ⚠️ La formulación de este apartado —«*grokking*», el circuito de reconocimiento de patrones, la
> distinción entre aprendizaje y contenido— resume una lectura extendida y comúnmente aceptada
> del libro en la literatura de diseño de juegos. Esta sesión no pudo abrir el texto completo del
> libro ni una página del autor con el contenido desarrollado (`raphkoster.com` respondió 200 a
> una comprobación de cabecera pero no sirvió el cuerpo de la página en los reintentos; la ficha
> del libro en Wikipedia — `en.wikipedia.org/wiki/A_Theory_of_Fun_for_Game_Design`, HTTP 200 — solo
> confirma la autoría y no desarrolla la tesis): trátalo como una síntesis fiable del canon, no
> como una cita textual del libro.

### 2.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Por qué un sistema deja de ser divertido aunque siga «funcionando» igual de bien |
| Pregunta de diagnóstico | ¿Qué patrón nuevo aprende el jugador en los próximos 10 minutos de juego? Si no hay respuesta, ahí es donde se aburre |
| Se aplica cuando | Diseñas la curva de contenido de un juego largo, o investigas por qué un sistema que probó bien en el minuto 5 cansa en el minuto 30 |
| No sirve para | Explicar la tensión narrativa, el vínculo social o el placer sensorial puro — para eso, MDA (`Fellowship`, `Sensation`) y las lentes de Schell del §4 |
| Ejemplo | Un roguelike se rejuega porque cada partida presenta una combinación de patrones distinta (sinergias de objetos); un *idle clicker* sin variación de patrón agota su gracia en minutos, y por eso su enganche real está en otro sitio: el bucle de vuelta (`13 · 01 §2.1`, el «bucle de meta») |

### 2.3 · Qué te hace hacer distinto mañana

- Antes de añadir contenido nuevo (un nivel más, un enemigo más del mismo tipo), pregúntate si
  añade un **patrón** nuevo o solo repite uno ya aprendido con otro sprite. Si es lo segundo, el
  coste de producción no compra diversión, compra duración.
- Cuando un playtester diga «se hace repetitivo», tradúcelo a Koster antes que a MDA: **¿qué
  patrón ya agotó?** La respuesta señala directamente qué sistema necesita una variación o un
  sistema nuevo que lo cruce (la «regla del segundo sistema» de `13 · 01 §1.5`).
- Diseña la curva de dificultad como una curva de **patrones nuevos por minuto**, no solo de
  números que suben (`13 · 01 §3.2`): la sensación de progreso viene de aprender, no de que el
  enemigo tenga más vida.
- Acepta que un sistema puede «vaciarse» de gracia para un jugador experto sin que esté roto —
  es la razón de fondo por la que la meta-progresión (`13 · 16 §2.3`) necesita ofrecer algo que
  **cambie cómo juegas**, no solo un número más grande: un número más grande no es un patrón
  nuevo, así que no reactiva el aprendizaje.
- Cuando prototipes (`13 · 01 §6`), pregunta explícitamente: «¿qué le sorprende a alguien que ya
  domina el prototipo anterior?». Si nada, el prototipo no añade nada que Koster explicaría como
  divertido, por muy bien producido que esté.

---

## 3 · Salen & Zimmerman — el juego como sistema y el juego significativo

### 3.1 · El marco

Katie Salen y Eric Zimmerman publicaron *Rules of Play: Game Design Fundamentals* (MIT Press,
2003), organizado en cuatro bloques —*Core Concepts*, *Rules*, *Play*, *Culture*— que tratan el
juego simultáneamente como **sistema formal** (reglas, componentes, sus relaciones internas),
como **experiencia de juego** (lo que el jugador vive al jugar) y como **fenómeno cultural** (lo
que el juego significa fuera de sí mismo). Es el marco más amplio de los nueve: no compite con
MDA, lo envuelve — MDA describe la mecánica de la mitad *Rules*, y este marco añade las otras dos.

Dos ideas de aquí valen su peso en oro para cualquier diseño:

**El círculo mágico** (tomado de Johan Huizinga y reformulado por los autores) describe **el
espacio dentro del cual transcurre el juego**: al entrar en él, el jugador adopta una **actitud
lúdica** (*lusory attitude*, término que toman de Bernard Suits) — acepta las reglas arbitrarias
del juego porque quiere jugar, no porque tengan sentido fuera de él. El dinero de *Monopoly* solo
vale dentro del círculo; fuera de él, es papel de colores. Este concepto explica algo que MDA no
explica: **por qué una regla arbitraria («no puedes moverte en diagonal») no rompe la ilusión**,
mientras que una regla que se siente injusta sí la rompe: la primera vive dentro del círculo
aceptado, la segunda lo agrieta.

La segunda idea es el **juego significativo** (*meaningful play*), que los autores plantean como
**el objetivo declarado de todo buen diseño**: una jugada es significativa cuando la relación
entre lo que el jugador hace y lo que el sistema le devuelve es **reconocible** (el jugador
entiende que su acción causó ese resultado) y **está integrada** en el resto de la partida (ese
resultado importa más adelante, no se queda aislado). Es, en otras palabras, el marco teórico en
el que vive la regla operativa de decisiones interesantes que ya tienes en
[13 · 01 §2.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#23--probarlo-sin-motor):
una decisión solo es interesante si sus consecuencias son visibles y encajan en algo más grande.

> ⚠️ La formulación exacta de «*discernible and integrated*» con la que el libro define
> *meaningful play* no se pudo verificar palabra por palabra esta sesión: MIT Press bloqueó el
> acceso a la ficha del libro (HTTP 403) y el artículo de Wikipedia
> (`en.wikipedia.org/wiki/Rules_of_Play`, HTTP 200, consultado en vivo) confirma que el concepto
> es «*the goal of successful game design*» y describe el círculo mágico («*using it to describe
> the space within which a game takes place*») y la actitud lúdica, pero no reproduce la
> definición formal completa. La paráfrasis de este apartado es fiel al consenso del campo, no
> una cita textual.

### 3.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Por qué una regla arbitraria funciona y otra se siente injusta; cuándo una decisión del jugador «cuenta» de verdad |
| Pregunta de diagnóstico | De esta acción del jugador, ¿ve con claridad que la causó él, y le importa dentro de tres minutos? Si falta cualquiera de las dos, no es *meaningful play* |
| Se aplica cuando | Diseñas feedback (¿se nota que fue el jugador quien lo hizo?) o decides si una elección cosmética debería tener peso mecánico |
| No sirve para | Medir si un sistema motiva a largo plazo — para eso, SDT (§5); ni para decidir a quién sirve el juego — para eso, Bartle/Quantic Foundry (§6) |
| Ejemplo | En *Monopoly*, comprar una propiedad es *meaningful*: se ve quién la compró (discernible) y afecta a todas las rondas siguientes (integrada). Elegir el color de tu ficha no lo es: no tiene ninguna consecuencia posterior |

### 3.3 · Qué te hace hacer distinto mañana

- Antes de dar por buena una elección de personalización (color, nombre, skin), pregúntate si es
  **puramente cosmética** o si el jugador espera que tenga peso — si el juego la trata como
  decisión pero no cambia nada, estás rompiendo el círculo mágico sin darte cuenta.
- Cuando una regla te parezca «rara mientras la explicas» pero funcione en la mesa, no la
  cambies por instinto: puede que viva perfectamente dentro del círculo mágico aceptado y solo
  suene mal fuera de él. Pruébala jugada, no explicada (conecta con la «prueba de papel» de
  `13 · 01 §2.3`).
- Audita tu HUD y tu feedback visual con la pregunta de discernibilidad: si el jugador no puede
  señalar **qué acción suya** produjo un resultado, arregla el feedback antes que la mecánica —
  el problema puede no ser el sistema, sino que no es discernible.
- Para cada sistema nuevo, comprueba que sus resultados **se integran** en algo posterior (otro
  sistema, una decisión futura, una consecuencia visible más adelante). Un resultado que no se
  integra en nada es la señal de la «regla del segundo sistema» de `13 · 01 §1.5` aplicada al
  revés: un sistema que no habla con ningún otro no es *meaningful*, es ruido.
- Cuando definas los pilares de diseño (`13 · 14 §1.3`), redacta al menos uno en términos de
  *meaningful play*: qué decisión quieres que el jugador sienta como propia y con peso, no solo
  qué estética persigues.

---

## 4 · Schell — la Tétrada Elemental y las lentes

### 4.1 · El marco

Jesse Schell propone en *The Art of Game Design: A Book of Lenses* (Morgan Kaufmann, 2008; 3.ª
ed., CRC Press, 2019) dos herramientas complementarias. La primera es la **Tétrada Elemental**:
todo juego está hecho de cuatro elementos —**mecánica**, **historia**, **estética** y
**tecnología**— que se apoyan entre sí como las cuatro patas de una mesa; tocar una sin pensar en
las otras tres produce un juego descompensado (un motor gráfico brillante sin mecánica que lo
sostenga, o una mecánica sólida contada con una historia que la contradice).

La segunda, y la que da nombre al libro, son las **lentes**: la página del propio libro las
describe como *«a cognitive framework — essentially a specific perspective or a mental
checklist»* — más de cien filtros de perspectiva distintos (la propia web dice *«over 100 distinct
perspective filters»*), cada uno formulado como una o varias preguntas que fuerzan a mirar el
diseño desde un ángulo concreto. No son reglas: son **herramientas de diagnóstico**. Cuando una
mecánica se siente aburrida o injusta y no sabes por qué, aplicar la lente correcta —por ejemplo,
la **Lente del Riesgo**, verificada en vivo esta sesión, que empuja a evaluar si las decisiones
del jugador tienen consecuencias significativas— suele señalar la causa en segundos.

### 4.2 · Un subconjunto operativo de 18 lentes

No hace falta memorizar el centenar completo. Esta lista cubre los ángulos que más se repiten en
un proyecto de tamaño pequeño-mediano; úsala como checklist antes de dar un sistema por cerrado:

| Lente | Pregunta que fuerza a hacerte |
|---|---|
| **De la experiencia esencial** | ¿Cuál es la experiencia que de verdad quiero que viva el jugador, más allá del tema o la mecánica? |
| **De la Tétrada Elemental** | ¿Las cuatro patas —mecánica, historia, estética, tecnología— se sostienen entre sí, o hay una que contradice a las demás? |
| **Del juguete** ⚠️ | Sin ningún objetivo, ¿es interesante manipular el sistema solo por manipularlo? |
| **De la curiosidad** | ¿Qué preguntas se hace el jugador mientras juega, y cuáles respondo yo y cuáles dejo abiertas? |
| **De la sorpresa** ⚠️ | ¿Dónde está lo inesperado, y por qué funciona (o no) en este contexto? |
| **De la diversión** ⚠️ | ¿Qué tipo de placer (de los ocho de MDA, `13 · 01 §1.3`) persigo con este sistema en concreto? |
| **Del riesgo** *(verificada en vivo)* | ¿Tienen las decisiones del jugador consecuencias que de verdad importan? |
| **De la justicia** ⚠️ | ¿Se percibe el resultado como consecuencia de las propias decisiones, o como un capricho del sistema? |
| **De la resonancia** ⚠️ | ¿Hay algo en este sistema que conecte con una experiencia real del jugador, más allá de la ficción del juego? |
| **De la habilidad** ⚠️ | ¿Qué habilidades —físicas, mentales, sociales— exijo, y coinciden con las que el juego dice enseñar? |
| **De la competencia** ⚠️ | Si hay rivalidad, ¿se siente justa y da ganas de mejorar, o solo frustra? |
| **De la cooperación** ⚠️ | Si hay cooperación, ¿los jugadores se necesitan de verdad o juegan en paralelo? |
| **De la comunidad** *(verificada en vivo)* | ¿Qué hace este sistema por la relación entre quienes juegan, más allá de la partida individual? |
| **Del reto** *(verificada en vivo, como «Lens of Challenge»)* | ¿Sé identificar qué es lo que los jugadores van a encontrar retador, y por qué lo será? |
| **De la economía** *(verificada en vivo, citada por el propio sitio)* | ¿Entiendo el flujo completo de recursos de este sistema, o solo la parte que programé primero? |
| **De la elegancia** ⚠️ | ¿Cuántas situaciones distintas salen de estas reglas? (Es la misma pregunta que el cociente de `13 · 01 §1.6`) |
| **De la unificación** ⚠️ | ¿Este sistema refuerza el tema del juego, o es una mecánica prestada de otro género sin más? |
| **De la infinita inspiración** ⚠️ | Antes de inventar desde cero: ¿qué de la vida real, no de otros juegos, podría inspirar esto? |

> ⚠️ Las lentes marcadas se citan por su nombre habitual en la literatura de diseño y en
> traducciones y resúmenes del libro ampliamente distribuidos; **no** se abrieron esta sesión
> contra el texto original. Las tres marcadas «verificada en vivo» —Riesgo, Comunidad y Reto (más
> la mención de Economía)— se comprobaron hoy contra `schellgames.com/art-of-game-design`
> (HTTP 200). La Tétrada Elemental y la Lente del Flow, citadas en `13 · 01 §3.1`, ya están
> verificadas ahí contra el texto de la 1.ª edición — no se repite esa verificación aquí.

### 4.3 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Cómo diagnosticar un problema de diseño desde ángulos concretos cuando «no sé qué falla» no lleva a ningún sitio |
| Pregunta de diagnóstico | De este sistema, ¿sostienen sus cuatro patas (mecánica/historia/estética/tecnología) el peso por igual? |
| Se aplica cuando | Un sistema «no se siente bien» y necesitas una lista de preguntas concretas, no una intuición vaga |
| No sirve para | Sustituir el playtest — las lentes orientan qué mirar, no dicen si funciona; eso lo dice `13 · 01 §7` |
| Ejemplo | Un puzzle técnicamente correcto que aburre: la Lente del Riesgo revela que ninguna decisión del jugador tiene consecuencia (todo movimiento es reversible sin coste) |

### 4.4 · Qué te hace hacer distinto mañana

- Antes de programar un sistema nuevo, pásalo por la **Tétrada**: escribe en una línea qué aporta
  a la mecánica, a la historia (aunque sea mínima), a la estética y a qué exige de la tecnología.
  Si una casilla queda en blanco, ese es el riesgo del sistema, no una casualidad.
- Cuando un playtest te deje sin diagnóstico claro («no sé, algo no cuadra»), elige **tres
  lentes** de la tabla de arriba antes de tocar el código — no las dieciocho, tres — y aplícalas
  por escrito. El acto de escribir la respuesta suele revelar la mecánica responsable.
- Añade la **Lente del Riesgo** a tu checklist de cada sistema de decisión (tiendas, mejoras,
  ramas de diálogo): si una elección no tiene consecuencia visible, no es una elección, es un menú.
- Usa la **Lente de la Elegancia** como criterio de corte antes de añadir un sistema nuevo: si no
  puedes decir con qué otro sistema existente hablará, no lo añadas todavía (`13 · 01 §1.6`).
- Guarda las lentes que uses en la **ficha por sistema** (`13 · 01 §8.2`): añade una fila
  «Lentes aplicadas» junto a «Casos borde» — deja rastro de qué ángulo ya revisaste para no
  repetir la misma pregunta en cada iteración.

---

## 5 · La teoría de la autodeterminación — por qué motiva un sistema

### 5.1 · El marco

La **Self-Determination Theory** (SDT), de Edward Deci y Richard Ryan, es un marco de psicología
de la motivación humana —no nació para juegos— que sostiene que la motivación intrínseca y el
bienestar dependen de satisfacer tres necesidades psicológicas básicas. Según la propia
organización de los autores, es *«a broad framework for the study of human motivation and
personality»*, y las tres necesidades son:

- **Autonomía**: sentir que uno actúa por iniciativa propia, no forzado. En SDT, «*the
  individual's experience of autonomy, competence, and relatedness*» es la condición que produce
  las formas más «volitivas» (elegidas de verdad) de motivación.
- **Competencia**: sentir que se domina un desafío. El marco la describe en el sentido de
  «*mastering ambient challenges*» — no basta con tener éxito, hace falta **sentir** que el éxito
  refleja habilidad propia.
- **Relación** (*relatedness*): la necesidad de conexión con otros, definida como «*the
  development and maintenance of close personal relationships*» y de pertenencia a un grupo.

La cláusula que hace operativo el marco es esta: **si a una de las tres se le priva, hay un coste
funcional medible** («*if any is thwarted there will be distinct functional costs*») — no se
compensan entre sí. Un juego que da muchísima competencia (números que suben sin parar) pero cero
autonomía (un único camino obligatorio) no motiva el doble por tener el doble de refuerzo: motiva
menos, porque una de las tres patas está coja.

Brian Rigby y Richard Ryan trasladaron SDT a videojuegos con el modelo **PENS** (*Player
Experience of Need Satisfaction*), publicado en su trabajo de consultoría e investigación de
Immersyve — la propia empresa, fundada por Deci y Ryan, describe su trabajo en torno a los
*«core principles of motivation, basic need satisfaction, and sustained engagement»* aplicados a
producto. La idea de PENS es medir, para un juego concreto, cuánta autonomía, competencia y
relación ofrece realmente, en vez de asumir que «tiene niveles y multijugador» ya lo cubre todo.

> ⚠️ El detalle exacto del modelo PENS —sus ítems de medición, si incluye «presencia» como cuarta
> dimensión— no se pudo verificar contra un artículo académico de Rigby y Ryan esta sesión:
> `immersyve.com` (HTTP 200, consultado en vivo) confirma la filiación de sus fundadores con SDT y
> el enfoque en «satisfacción de necesidades básicas», pero la página no desarrolla el modelo con
> el detalle necesario para citarlo con precisión. Trátalo como una extensión razonable de SDT a
> juegos, no como una cita textual de PENS.

### 5.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Por qué un sistema motiva más allá del refuerzo numérico — o deja de motivar aunque el número siga subiendo |
| Pregunta de diagnóstico | De este sistema: ¿da elección real (autonomía)? ¿el jugador puede sentir que mejora por sí mismo (competencia)? ¿conecta con otras personas de algún modo (relación)? |
| Se aplica cuando | Diseñas progresión, recompensas, dificultad o cualquier sistema pensado para «enganchar» a largo plazo |
| No sirve para | Explicar por qué una mecánica de acción concreta se siente bien en el momento — eso es *game feel* (`04 · 15`), no motivación a largo plazo |
| Ejemplo | Un tutorial obligatorio de 20 minutos sin poder saltarlo mata autonomía desde el minuto uno, por muy bien que enseñe la competencia que viene después |

### 5.3 · Qué te hace hacer distinto mañana

- En cada sistema de progresión, escribe explícitamente cuál de las tres necesidades sirve
  **de forma principal**. Si un sistema entero (digamos, la XP) solo sirve a competencia y nunca
  a autonomía, busca dónde meter una elección real, aunque sea pequeña (elegir qué mejorar antes).
- Revisa el onboarding (`13 · 01 §5`) con la lente de la autonomía: un tutorial que no se puede
  saltar, con un único camino y sin margen de error, maximiza aprendizaje a corto plazo pero
  hipoteca la motivación — decide ese coste a propósito, no por descuido.
- Para dar competencia real (no solo la sensación de ella), asegúrate de que el jugador tiene
  **feedback claro de que mejoró** — no solo de que ganó. Ganar por suerte no da competencia;
  ganar viendo que jugaste mejor que la vez anterior, sí.
- Si tu juego es solo un jugador, no descartes la relación: los créditos que mencionan a quien
  ayudó a testear, un sistema de fantasmas o récords comparables, o simplemente compartir una
  captura al final, dan algo de relación sin necesitar multijugador.
- Añade un campo «Necesidad SDT que sirve» a la **ficha por sistema** de
  [13 · 01 §8.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#82--ficha-por-sistema--plantilla):
  si al rellenarla ves que todos tus sistemas sirven a la misma necesidad, tienes un desequilibrio
  de motivación que ningún playtest corto va a detectar (SDT predice que se nota a las horas, no
  a los minutos).

---

## 6 · Bartle y Quantic Foundry — para quién diseñas

### 6.1 · Bartle: los cuatro tipos, y su propia advertencia

Richard Bartle publicó en 1996 *Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs*,
proponiendo cuatro arquetipos de jugador sobre dos ejes: **actuar / interactuar** y **orientado al
mundo / orientado a otros jugadores**.

| Tipo | Eje | Busca | Cita del propio texto |
|---|---|---|---|
| **Triunfadores** (*Diamonds*) | Actuar + mundo | Progreso y logro | *«Achievement within the game context»* |
| **Exploradores** (*Spades*) | Interactuar + mundo | Descubrir el sistema | *«Exploration of the game»*, mapear su topología, experimentar con su física |
| **Socializadores** (*Hearts*) | Interactuar + jugadores | Relación con otros | *«Socialising with others»*, relaciones entre jugadores |
| **Asesinos** (*Clubs*) | Actuar + jugadores | Imponerse sobre otros | *«Imposition upon others»*, causar molestia a otros jugadores |

Lo que casi nadie cita es la **advertencia del propio Bartle**, verificada hoy contra el texto
original en `mud.co.uk/richard/hcds.htm`: *«these notes concern stereotypical players, and are
not to be assumed to be true of any individual player»*; el análisis *«takes no account of
outside factors»*; y el propio autor admite que su enfoque no es *«conventionally rigorous»*,
reconociendo no ser psicólogo entrenado. **El modelo nació para describir la dinámica social de
un MUD de texto de los años 90**, no como un test de personalidad universal — usarlo para
encasillar a un jugador concreto es exactamente el mal uso que el propio Bartle señaló.

### 6.2 · Quantic Foundry: el modelo empírico moderno

Quantic Foundry sustituye los cuatro tipos por un modelo con **datos de cientos de miles de
encuestas**: 6 clústeres y 12 motivaciones (entre ellas *Action*, *Social*, *Mastery*, *Achievement*,
*Immersion*, *Creativity*), pensado para explicar **por qué** alguien juega, no solo qué hace.

> ⚠️ `quanticfoundry.com` devolvió HTTP 403 en todos los intentos de esta sesión (con y sin
> cabecera de navegador) — bloqueo de tráfico automatizado, coherente con lo que ya reportó
> `_indice/auditorias/diseno-gdd.md`. La descripción de los 6 clústeres / 12 motivaciones de este
> apartado procede del conocimiento general del campo, **no** de una lectura en vivo del sitio
> esta sesión: si necesitas los nombres exactos y actuales de cada clúster para un documento
> formal, ábrelo tú mismo antes de citarlo con precisión.

### 6.3 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | A qué tipo de jugador sirve una mecánica, y a cuál deja fuera a propósito |
| Pregunta de diagnóstico | Si tuviera que elegir un único tipo de jugador al que servir mejor que nadie, ¿cuál sería, y qué mecánica actual **no** le sirve? |
| Se aplica cuando | Decides qué sistemas priorizar con presupuesto limitado, o intentas entender por qué una función que «debería gustar a todos» no engancha a nadie |
| No sirve para | Perfilar a un jugador individual ni diseñar personajes o narrativa — es una herramienta de público, no de personalidad |
| Ejemplo | Un roguelike con generación procedural (`04 · 05`) sirve de forma natural a exploradores y triunfadores; si además quieres servir a socializadores, necesitas un sistema ajeno al bucle central (marcadores compartidos, semillas de nivel para comparar partidas), no forzar el roguelike a ser social |

### 6.4 · Qué te hace hacer distinto mañana

- Antes de diseñar un sistema «para enganchar a todo el mundo», elige **un** tipo de jugador
  objetivo y dilo en voz alta. Un juego que sirve a todos por igual normalmente no sirve a nadie
  mejor que la competencia.
- Nunca uses el test de Bartle para encasillar a una persona concreta («mi hermano es un
  asesino») — el propio autor lo desaconseja. Úsalo para describir **mecánicas**, no personas: «el
  PvP libre sirve al arquetipo asesino», no «Fulano es un asesino».
- Añade telemetría que mida **comportamiento observado**, no motivación declarada: cuenta qué
  verbos usa cada jugador de verdad (exploración vs combate vs interacción social) — es más
  fiable que preguntarle qué tipo de jugador cree ser.
- Si tu presupuesto solo da para un sistema social o uno competitivo, decide con criterio de
  público objetivo, no por moda de género: un juego de exploración solitaria (metroidvania,
  `04 · 06`) puede no necesitar nunca un sistema social — decirlo explícitamente ahorra meses.
- Documenta en el GDD de una página (`13 · 01 §8.1`, campo «Referencias y qué tomo de cada una»)
  a qué tipo de jugador sirve tu juego, y qué tipo queda **deliberadamente** fuera. Es una
  decisión de diseño, no un olvido.

---

## 7 · Costikyan — la incertidumbre como ingrediente de diseño

### 7.1 · El marco

Greg Costikyan dedicó buena parte de su obra teórica a un único argumento: **la incertidumbre no
es un defecto que tolerar, es el ingrediente que hace jugable un juego.** En su charla de GDC
Austin 2009, *Randomness: Blight or Bane?* (verificada en vivo, `costik.com`), lo desmonta pieza
a pieza:

**La dicotomía «juego de habilidad frente a juego de azar» es falsa.** Casi todo juego real es una
mezcla: hasta un tirador en primera persona tiene daño parcialmente aleatorio bajo el capó, y el
Póker —que parece puro azar— convierte esa aleatoriedad en profundidad estratégica real a través
de las rondas de apuestas: *«the strategy of Poker is based on its randomness»*.

**La regresión a la media es la herramienta que domestica el azar.** Cuantas más pruebas
aleatorias independientes tenga una partida, menos determina el resultado el azar y más lo
determina la estrategia: *«the more random tests, the lower the likelihood that the outcome will
be at one extreme»*. Por eso un solo tiro de dado decide un 50/50 puro, pero cien tiradas con algo
de estrategia de por medio casi siempre las gana el mejor jugador. Esto tiene una consecuencia de
diseño directa: **si quieres que el azar decida poco, dale muchas oportunidades pequeñas en vez de
una sola grande.**

Costikyan describe además **tres usos deliberados** del azar, cada uno con su propia lógica:

1. **Fidelidad de simulación.** La guerra real es impredecible («*no battle plan survives contact
   with the enemy*»); un wargame sin azar es, por eso, una simulación peor, no una más pura.
2. **Romper la simetría a bajo coste.** Dos jugadores en igualdad de condiciones (`Ajedrez`, `Go`)
   solo generan una partida interesante si el juego tiene profundidad estratégica suficiente para
   que la simetría se rompa sola; si no la tienes (`Hex`, según su propio ejemplo, tiene solución
   óptima demostrada), el azar en el reparto inicial (cartas de ruta en *Ticket to Ride*, el
   trazado de *Catan*) rompe la simetría sin necesitar la profundidad de un *Go*.
3. **Nivelar el terreno de juego** para partidas asimétricas en habilidad (un adulto contra un
   niño en *Snakes and Ladders*) o **dar variedad de encuentro** sin coste de producción
   (generación procedural en roguelikes: *«no two play sessions are identical»*).

Y dos técnicas concretas para que el azar **no** decida la partida a pesar de usarlo: que los
resultados posibles sean de **valor equivalente** entre sí (las cartas de acción de *Torres*, donde
ninguna es objetivamente mejor) y que el azar **afecte a todos los jugadores por igual**, como el
clima (la bolsa compartida de *Medici*, de la que todos compran del mismo lote).

> 💡 **Una distinción muy citada en el oficio —el azar de entrada (*input randomness*, antes de
> decidir) frente al azar de salida (*output randomness*, después de decidir)—** no se pudo
> verificar esta sesión contra una fuente primaria abierta en vivo (se intentó una URL de Mark
> Rosewater, diseñador jefe de *Magic: The Gathering*, sin éxito). ⚠️ Trátala como terminología de
> uso extendido, no como una cita de Costikyan: la distinción que **sí** está verificada arriba —
> azar que rompe simetría al empezar frente a azar que resuelve una acción durante la partida— es
> equivalente en la práctica y es la que debes usar si necesitas citar la fuente con precisión.

### 7.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Cuándo el azar mejora un diseño y cuándo lo arruina; cómo usarlo sin que decida la partida |
| Pregunta de diagnóstico | Este resultado aleatorio, ¿lo sufren todos los jugadores por igual, tiene un valor comparable al resto de resultados posibles, y hay suficientes tiradas para que la estrategia domine a largo plazo? |
| Se aplica cuando | Diseñas *loot*, generación procedural, combate con crítico, o cualquier tabla de probabilidad |
| No sirve para | Decidir *cuánta* variedad numérica necesita una curva de progresión — eso es `13 · 01 §4.4` y `13 · 13 §8` |
| Ejemplo | Una bolsa aleatoria sin memoria en un *loot* de jefe (`13 · 13 §5`, ya implementada) es azar «de salida» clásico: cada jugador se enfrenta al mismo jefe, pero el resultado varía; usar la misma semilla de nivel para todos en un modo diario reparte el mismo azar «de entrada» a todo el mundo por igual |

### 7.3 · Qué te hace hacer distinto mañana

- Antes de añadir un elemento aleatorio, decide **para qué de los tres usos** lo añades
  (simulación, ruptura de simetría o variedad/nivelación). Si no sabes contestar, probablemente
  el azar está ahí «porque los juegos tienen dados», que es la razón más débil de todas.
- Cuando un playtester diga que el azar «es injusto», comprueba primero si el problema es de
  **regresión a la media**: quizá una sola tirada decide demasiado, y la solución no es quitar el
  azar sino repartirlo en más tiradas pequeñas (varios golpes con daño variable en vez de un único
  golpe crítico que decide el combate).
- Si usas azar para romper simetría al inicio de una partida (cartas iniciales, semilla de nivel,
  posiciones de aparición), audita que **todos los resultados posibles tengan valor comparable** —
  si una combinación inicial es objetivamente mejor que otra, no rompiste la simetría con
  elegancia, la rompiste con suerte.
- Distingue explícitamente, en tu documento de sistema (`13 · 01 §8.2`), el azar que **resuelve
  una acción del jugador** (daño variable, crítico) del azar que **genera contenido antes de
  jugar** (mapa, semilla, loot table) — tienen implicaciones de diseño y de QA distintas, y
  mezclarlos en la misma fila de la ficha esconde el problema real cuando algo sale mal.
- Antes de descartar un sistema por «demasiado aleatorio», comprueba si su función es
  **nivelar el terreno** (un minijuego para todas las edades) o **dar variedad de encuentro sin
  coste** (contenido procedural): en esos dos casos, más azar puede ser la decisión correcta, no
  un defecto que corregir.

---

## 8 · Dominancia estratégica y mecánicas transitivas/intransitivas

### 8.1 · El marco

Ian Schreiber, en su serie *Game Balance Concepts* (2010), da el vocabulario preciso que
`13 · 01 §1.4` y `§2.3` ya usan de forma intuitiva («si una opción gana siempre, bórrala»):

**Mecánica transitiva**: una jerarquía clara donde *«some things are just flat out better than
others in terms of their in-game effects»* — un objeto A es objetivamente superior a B en todos
los contextos. No es un defecto en sí: **toda progresión de poder es transitiva por diseño** (un
arma de nivel 10 debe ser mejor que una de nivel 1). El peligro aparece cuando dos opciones
**deberían** competir en el mismo nivel de coste y una gana siempre: *«a sufficiently overpowered
object ruins the balance of the entire game»*, porque se vuelve la opción inevitable y el resto
decora.

**Mecánica intransitiva**: el equivalente a piedra-papel-tijera — *«no hay una única estrategia
dominante, porque todo puede ser derrotado por algo más»*. Aquí no hay jerarquía: cada opción gana
en un contexto y pierde en otro, que es exactamente la definición de decisión interesante de
Salen & Zimmerman (§3) y de `13 · 01 §2.3`.

Una **estrategia dominante** es la opción que gana en todo contexto sin excepción — el fallo de
diseño que ambos marcos, desde ángulos distintos, llaman a cazar. Schreiber da un método concreto
de tres pasos, verificado hoy en vivo contra el blog original:

1. **Construir la matriz de pagos**: una tabla de resultados para cada combinación de opciones
   enfrentadas (arma A contra arma B, unidad X contra unidad Y).
2. **Eliminación iterativa de dominadas**: *«si una fila es estrictamente mejor que otra en todas
   las situaciones, esa estrategia está dominada»* — bórrala de la matriz y repite; lo que quede
   al final es el conjunto de opciones realmente viables.
3. **Ajustar el coste, no solo el poder**: la solución casi nunca es debilitar la opción dominante
   a ciegas (eso es «nerfear sin datos»); es *«cambiar los costes relativos y la disponibilidad»*
   para que la mezcla óptima entre opciones se reparta — por ejemplo, si un ejército óptimo
   resulta ser 30 % arqueros / 50 % infantería / 20 % voladores, el coste de cada unidad es lo que
   hay que ajustar para acercarse a esa proporción, no borrar arqueros del juego.

### 8.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Por qué «todos usan lo mismo» y cómo arreglarlo sin nerfear a ciegas |
| Pregunta de diagnóstico | Para cada par de opciones que deberían competir, ¿hay algún contexto real de partida en el que la opción B gane a la A? Si no lo hay para ninguna B, A es dominante |
| Se aplica cuando | Balanceas armas, unidades, cartas, builds o cualquier conjunto de opciones que compiten por el mismo presupuesto de coste |
| No sirve para | Progresión donde la jerarquía es intencionada (una espada de nivel 10 debe ganar a una de nivel 1) — ahí lo transitivo es correcto; el problema solo existe entre opciones del **mismo** nivel de coste |
| Ejemplo | La fila «Todos eligen lo mismo» de la tabla de diagnóstico de `13 · 01 §1.4` es exactamente una estrategia dominante detectada por sus síntomas; este apartado da el método para cazarla con una matriz, no solo por intuición de playtest |

### 8.3 · Qué te hace hacer distinto mañana

- Para cualquier conjunto de opciones al mismo nivel de coste (armas iniciales, cartas de la misma
  rareza, ramas de un árbol de habilidades del mismo tramo), construye la matriz de pagos antes de
  balancear a ojo — aunque sea una tabla de 4×4 a mano, cuesta veinte minutos y ahorra semanas de
  parches.
- Cuando midas con telemetría (`13 · 01 §9.5`, ya implementada) qué opción usa la gente, añade
  **tasa de uso por opción** como métrica junto a las de dificultad que ya recoges — una opción
  usada por el 90 % de las partidas es dominancia con nombre y apellido, no una preferencia sana.
- Antes de nerfear la opción dominante, prueba primero a **subir el coste** de las opciones
  dominadas o a **bajar el coste** de la dominante manteniendo su poder — ajustar el coste cambia
  la proporción óptima sin que ningún objeto deje de sentirse bien de usar.
- Diseña deliberadamente relaciones **intransitivas** (piedra-papel-tijera) entre categorías
  amplias del juego —tipos de daño, clases de unidad, arquetipos de mazo— y dentro de cada
  categoría deja que la progresión sea **transitiva** (mejor cuanto más avanzas). Mezclar los dos
  niveles con criterio evita tanto el «todo es igual de válido» como el «hay una build correcta».
- Documenta en la ficha de sistema (`13 · 01 §8.2`) qué opciones **deberían** competir entre sí al
  mismo coste, para que la próxima persona (o tú, dentro de tres meses) sepa contra qué construir
  la matriz de pagos sin tener que redescubrirlo jugando cien partidas.

---

## 9 · Juul — emergencia frente a progresión

### 9.1 · El marco

Jesper Juul, en *Half-Real: Video Games between Real Rules and Fictional Worlds* (MIT Press,
2005) y en el ensayo previo *The Open and the Closed: Games of Emergence and Games of
Progression* (verificados en vivo hoy en `jesperjuul.net` y `half-real.net`), propone la
distinción canónica entre dos formas de generar variación en un juego:

**Juegos de emergencia**: *«a number of simple rules combine to form interesting variation»* — el
diccionario de *Half-Real* lo resume como *«variation appears by the interaction between
elements in the game»*, hasta el punto de que *«emergence games often surprise players and even
the designers of the game»*. Ajedrez, *Counter-Strike* o cualquier juego de estrategia en tiempo
real son juegos de emergencia: el diseñador construye las reglas, no las partidas.

**Juegos de progresión**: el jugador *«has to perform a predefined set of actions to complete the
game»* — el diccionario lo llama lo opuesto exacto: *«variation happens by introducing new
elements and features as the player progresses»*. Las aventuras gráficas clásicas son el ejemplo
citado en la propia fuente: *«adventure games are generally progression games, as they have to be
completed by performing exactly the actions that the game design dictates»*.

La consecuencia de diseño es económica, no solo estética: **la emergencia es reutilizable — genera
sus propias guías de estrategia — mientras que la progresión necesita contenido de autor para cada
tramo nuevo y tiene poca rejugabilidad** (un *walkthrough* la agota igual que un patrón agotado
agota a Koster en §2). Esto no es un juicio de valor: un juego puede, y casi siempre debe, ser
**ambos** en distinta proporción según la sección — el mismo argumento que ya cierra la fila de
diagnóstico «aburre a los diez minutos» de `13 · 01 §1.4`, aquí con nombre propio.

### 9.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Por qué un contenido generado se siente todo igual (falta emergencia) o por qué un mundo con reglas libres se siente vacío de dirección (falta progresión) |
| Pregunta de diagnóstico | ¿Esta sección del juego varía porque sus reglas interactúan entre sí, o porque yo, como diseñador, decidí a mano lo que pasa a continuación? Cualquiera de las dos respuestas es válida — la pregunta es si fue una decisión, no un accidente |
| Se aplica cuando | Diseñas generación procedural (`13 · 07`), decides cuánta narrativa lineal meter en un juego de sistemas, o un roguelike se siente repetitivo pese a la generación aleatoria |
| No sirve para | Medir dificultad ni motivación — es un eje sobre **de dónde sale la variación**, no sobre si es divertida (eso es Koster, §2) ni sobre si motiva a largo plazo (eso es SDT, §5) |
| Ejemplo | Un roguelike (`04 · 05`) es emergencia en la generación de mazmorras y progresión en la narrativa de meta-run que se desbloquea por capítulos; mezclar ambos a propósito es lo que le da tanto sorpresa como dirección |

### 9.3 · Qué te hace hacer distinto mañana

- Antes de generar contenido procedural, decide qué **reglas** interactúan entre sí para producir
  la variación (emergencia real) frente a qué simplemente **baraja** piezas de autor ya escritas
  (progresión disfrazada de aleatoria). Un generador que solo elige entre 5 salas prediseñadas al
  azar no es emergencia — es progresión con orden mezclado, y se agota igual de rápido.
- Si un sistema de emergencia se siente caótico o injusto, no le añadas más reglas: **audita las
  que ya tiene** para encontrar la interacción que produce el resultado no deseado. Añadir reglas
  a un sistema emergente que ya falla multiplica el espacio de casos, no lo simplifica.
- Si una sección se siente vacía pese a tener libertad total (mundo abierto sin dirección),
  considera inyectar **progresión deliberada**: un hilo narrativo, un gating por habilidad
  (`13 · 01 §5.3`), o simplemente un orden recomendado — no todo tiene que emerger.
- Al escribir el pitch de una mecánica nueva, decide y anota si es de emergencia o de progresión
  **antes** de programarla: cambia por completo cuánto contenido de autor necesitas y cuánta
  rejugabilidad puedes prometer sin producir contenido nuevo cada semana.
- Cuando el presupuesto de producción sea el problema (no hay tiempo para más niveles a mano),
  la palanca casi siempre es **más emergencia, no más progresión**: cruzar sistemas existentes
  (`13 · 01 §1.5`, la regla del segundo sistema) es más barato que escribir contenido lineal nuevo.

---

## 10 · Fullerton — elementos formales y diseño centrado en el juego

### 10.1 · El marco

Tracy Fullerton es la autora de *Game Design Workshop* (ya en su 5.ª edición, 2024), descrito por
su propio sitio —verificado en vivo hoy a través de una instantánea de archivo de
`gamedesignworkshop.com`— como *«a playcentric approach to creating innovative games»* que
*«demystifies the creative process with clear and accessible analysis of the formal and dramatic
systems of game design»*. Dos ideas separan este marco de los ocho anteriores:

**El diseño centrado en el juego** (*playcentric design*): el proceso de Fullerton no empieza por
el documento ni por el arte, empieza por **jugar el sistema lo antes posible**, aunque sea con
cajas y fichas, y decidir todo lo demás a partir de lo que esa mesa de pruebas enseña. Es el mismo
espíritu que ya tienes en `13 · 01 §6` (prototipado) y `§2.3` (prueba de papel), pero Fullerton lo
eleva a **método completo**: prototipar, jugar, evaluar y refinar en bucle, no como un paso previo
a «el diseño de verdad», sino como el diseño en sí.

**Los elementos formales**: antes de hablar de diversión o de estética, Fullerton pide describir
el juego como un sistema formal con ocho piezas — jugadores, objetivos, procedimientos, reglas,
recursos, conflicto, límites y resultado. Es la lista de comprobación más literal de los nueve
marcos: si no puedes rellenar las ocho casillas de tu propio juego, no tienes un diseño todavía,
tienes una idea.

| Elemento formal | Pregunta que responde |
|---|---|
| **Jugadores** | ¿Cuántos, y qué patrón de interacción tienen entre sí (individual, equipo, uno contra todos)? |
| **Objetivos** | ¿Qué define ganar, en una frase sin ambigüedad? |
| **Procedimientos** | ¿Qué acciones puede realizar el jugador, turno a turno o fotograma a fotograma? |
| **Reglas** | ¿Qué limita esos procedimientos? (Es la misma pregunta que `13 · 01 §1.1`, con otro nombre) |
| **Recursos** | ¿Qué tiene valor dentro del sistema, y de dónde sale? (`13 · 01 §4.1`) |
| **Conflicto** | ¿Qué se interpone entre el jugador y el objetivo? |
| **Límites** | ¿Dónde termina el círculo mágico de esta partida en concreto? (conecta directo con §3.1) |
| **Resultado** | ¿El resultado es siempre el mismo, o varía entre partidas? |

> ⚠️ La lista completa de ocho elementos formales (jugadores, objetivos, procedimientos, reglas,
> recursos, conflicto, límites, resultado) se cita según la caracterización habitual y muy
> extendida del libro en cursos y resúmenes de diseño de juegos. Esta sesión verificó en vivo la
> existencia del libro, su enfoque *playcentric* y la mención a «sistemas formales y dramáticos»
> (`gamedesignworkshop.com`, vía `web.archive.org`, y `tracyfullerton.com`, ambos HTTP 200), pero
> no pudo abrir el texto del libro para confirmar la lista exacta de ocho elementos palabra por
> palabra.

### 10.2 · Ficha operativa

| Campo | Contenido |
|---|---|
| Qué explica | Si tienes de verdad un diseño de juego completo, o solo una mecánica suelta sin sistema alrededor |
| Pregunta de diagnóstico | ¿Puedo rellenar las ocho casillas de la tabla de arriba para mi juego, en una frase cada una, sin dudar? |
| Se aplica cuando | Arrancas un proyecto nuevo, antes incluso del GDD de una página (`13 · 01 §8.1`), o cuando un prototipo no engancha y sospechas que falta una pieza formal entera |
| No sirve para | Decidir si el diseño es *bueno* — solo si está *completo*. Un diseño con las ocho casillas rellenas puede seguir siendo aburrido; para eso están Koster (§2) y las lentes de Schell (§4) |
| Ejemplo | Un prototipo con mecánica sólida pero sin **límites** claros (¿cuándo termina una partida?) se siente inacabado aunque la jugabilidad esté bien — el elemento formal que falta señala exactamente qué falta decidir |

### 10.3 · Qué te hace hacer distinto mañana

- Antes de escribir el GDD de una página (`13 · 01 §8.1`), rellena primero las ocho casillas de
  elementos formales en una frase cada una. Si alguna se resiste, ese es el hueco real del diseño,
  no un detalle que «ya se verá jugando».
- Adopta el ciclo *playcentric* como rutina, no como excepción: prototipo → jugarlo tú mismo →
  evaluarlo con una pregunta escrita de antemano (`13 · 01 §6.1`) → refinar. Un diseño que nunca
  se ha jugado, ni por ti, no es un diseño: es una hipótesis sin probar.
- Cuando un elemento formal cambie (añades un jugador más, cambias el objetivo), revisa **todos
  los demás**: los ocho elementos se sostienen entre sí igual que la Tétrada de Schell (§4) — un
  cambio de objetivo casi siempre obliga a revisar el conflicto y el resultado.
- Usa «Límites» como disparador de una pregunta que se olvida a menudo: ¿qué pasa exactamente
  cuando la partida termina? ¿Se puede volver a intentar sin fricción? Es la misma pregunta que
  `13 · 01 §5.4` hace sobre los primeros 60 segundos, aplicada al final en vez de al principio.
- Antes de invertir en arte o en contenido, comprueba el diseño formal con el prototipo más barato
  posible (cajas, papel, `13 · 01 §6.2`): Fullerton construyó el libro entero alrededor de la idea
  de que el sistema formal se puede —y se debe— probar antes de que exista ni una sola línea de
  GML.

---

## 11 · Cómo se traduce a GameMaker

Los nueve marcos son, sobre todo, preguntas que te haces antes y durante el diseño — no generan
mucho código propio. Lo que sí se traduce directamente a GameMaker son dos instrumentos de
medición que convierten «creo que…» en datos: **qué motiva de verdad** (Bartle/Quantic Foundry) y
**qué opción domina de verdad** (Schreiber). Ambos amplían la telemetría que ya tienes en
[13 · 01 §9.5-9.6](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#9--cómo-se-traduce-a-gamemaker)
en vez de reescribirla.

### 11.1 · Telemetría de motivación observada (Bartle / Quantic Foundry)

No preguntes qué tipo de jugador cree ser alguien: cuenta qué hace. Este contador clasifica cada
evento de juego en una de cuatro categorías amplias emparentadas con los cuatro tipos de Bartle —
combate (triunfador/asesino), exploración (explorador), colección (triunfador) y social
(socializador)— y se vuelca junto al resto de la telemetría ya existente.

```gml
/// scr_telemetria_motivacion — cuenta VERBOS, no preguntes por identidad de jugador
///              Cuatro categorías amplias emparentadas con Bartle (§6): no sustituyen una
///              encuesta si de verdad necesitas perfilar público objetivo, solo miden uso real.

/// @description Inicializa los contadores. Llamar una vez al arrancar la partida.
function motivacion_iniciar() {
    global.motivacion = {
        combate:     0,   // ataques y muertes causadas — triunfador / asesino
        exploracion: 0,   // salas nuevas visitadas — explorador
        coleccion:   0,   // objetos y secretos recogidos — triunfador
        social:      0    // interacciones con NPC o con otros jugadores — socializador
    };
}

/// @description Registra un evento de motivación. _categoria debe ser una de las cuatro claves
///              de global.motivacion; cualquier otra se ignora en vez de fallar.
function motivacion_registrar(_categoria) {
    if (!struct_exists(global.motivacion, _categoria)) {
        show_debug_message($"[motivacion] categoría desconocida: {_categoria}");
        return;
    }
    struct_set(global.motivacion, _categoria, struct_get(global.motivacion, _categoria) + 1);
}

/// @description Devuelve la categoría con más eventos: la motivación DOMINANTE observada
///              en esta sesión, no la que el jugador diría de sí mismo.
function motivacion_dominante() {
    var _nombres = struct_get_names(global.motivacion);
    var _mejor_nombre = _nombres[0];
    var _mejor_valor  = struct_get(global.motivacion, _mejor_nombre);

    for (var _i = 1; _i < array_length(_nombres); _i++) {
        var _valor = struct_get(global.motivacion, _nombres[_i]);
        if (_valor > _mejor_valor) {
            _mejor_valor  = _valor;
            _mejor_nombre = _nombres[_i];
        }
    }
    return _mejor_nombre;
}
```

Llama a `motivacion_registrar("exploracion")` cada vez que se pisa una sala por primera vez,
`motivacion_registrar("coleccion")` al recoger un secreto, y así con las otras dos. Con cientos de
sesiones agregadas (no con una sola: `13 · 01 §7.3`, cinco personas por ronda), la distribución de
`motivacion_dominante()` te dice a qué tipo de jugador está sirviendo tu juego **de verdad**, para
contrastarlo con a quién creías que estabas diseñando (§6.4).

### 11.2 · Telemetría de dominancia (Schreiber)

Este contador amplía la telemetría de `13 · 01 §9.5` para responder la pregunta de §8: de un
conjunto de opciones al mismo coste (armas, cartas, builds), ¿hay alguna que se elige casi
siempre? Se registra una vez por elección, y se lee al final de una ronda de playtests.

```gml
/// scr_telemetria_dominancia — ¿alguna opción se elige casi siempre? (13 · 15 §8)

/// @description Inicializa el contador de elecciones para un conjunto de opciones dado.
/// @param {Array<String>} _opciones  Nombres de las opciones a vigilar (mismo nivel de coste)
function dominancia_iniciar(_opciones) {
    global.dominancia = {};
    for (var _i = 0; _i < array_length(_opciones); _i++) {
        struct_set(global.dominancia, _opciones[_i], 0);
    }
}

/// @description Registra que el jugador eligió _opcion en esta partida.
function dominancia_registrar(_opcion) {
    if (!struct_exists(global.dominancia, _opcion)) return;
    struct_set(global.dominancia, _opcion, struct_get(global.dominancia, _opcion) + 1);
}

/// @description Vuelca a la consola la tasa de uso de cada opción sobre el total de partidas
///              registradas. Una opción por encima de UMBRAL_DOMINANCIA es sospechosa de
///              dominancia estratégica (§8.3): revisa su matriz de pagos antes de nerfear a ojo.
function dominancia_informe(_umbral = 0.60) {
    var _nombres = struct_get_names(global.dominancia);
    var _total   = 0;
    for (var _i = 0; _i < array_length(_nombres); _i++) {
        _total += struct_get(global.dominancia, _nombres[_i]);
    }
    if (_total == 0) {
        show_debug_message("[dominancia] sin datos todavía");
        return;
    }

    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _nombre = _nombres[_i];
        var _tasa   = struct_get(global.dominancia, _nombre) / _total;
        var _marca  = (_tasa >= _umbral) ? " ⚠ posible dominante" : "";
        show_debug_message($"[dominancia] {_nombre}: {string(round(_tasa * 100))}%{_marca}");
    }
}
```

`dominancia_informe()` no sustituye la matriz de pagos de §8.1 — la telemetría dice **qué**
sospechar, la matriz explica **por qué** y qué coste tocar. Es el mismo orden que ya usa
`13 · 01 §3.4`: medir primero con datos, diagnosticar después con el marco teórico correspondiente.

> Símbolos usados en esta sección, todos verificados con `buscar.py` contra el runtime
> `2026.0.0.23`: `struct_exists`, `struct_get`, `struct_set`, `struct_get_names`, `array_length`,
> `show_debug_message`, `round`, `string`.

---

## 12 · Tabla: qué marco usar para qué problema

| Síntoma o pregunta | Marco | Qué hacer |
|---|---|---|
| «Se hace repetitivo aunque no cambié nada» | **Koster** (§2) | Identifica qué patrón ya se agotó; añade uno nuevo o cruza sistemas (`13 · 01 §1.5`) |
| «No sé si esta regla rara va a funcionar» | **Salen & Zimmerman** (§3) | Pruébala jugada, no explicada: ¿vive bien dentro del círculo mágico? |
| «El sistema está bien pero algo no cuadra y no sé qué» | **Schell** (§4) | Aplica 3 lentes relevantes de la tabla del §4.2 y escribe la respuesta |
| «Engancha al principio y luego se apaga» | **SDT** (§5) | Revisa si sigue habiendo autonomía y competencia creciente, no solo refuerzo numérico |
| «Quiero que enganche a todo el mundo» | **Bartle / Quantic Foundry** (§6) | Elige un tipo de jugador objetivo; acepta que sirves peor a los demás a propósito |
| «El azar se siente injusto» | **Costikyan** (§7) | Comprueba regresión a la media, valor equivalente entre resultados y si el azar es de todos por igual |
| «Todo el mundo usa la misma arma / build / carta» | **Dominancia estratégica** (§8) | Matriz de pagos, eliminación iterativa, ajusta coste antes que poder |
| «Mi generación procedural se siente toda igual» | **Juul — emergencia** (§9) | Audita qué reglas interactúan de verdad; añade cruces, no más piezas |
| «El mundo abierto se siente vacío sin dirección» | **Juul — progresión** (§9) | Inyecta progresión deliberada: gating, hilo narrativo, orden recomendado |
| «No sé si tengo un diseño o solo una idea suelta» | **Fullerton** (§10) | Rellena las ocho casillas de elementos formales; lo que se resista es el hueco real |
| «No sé si esta decisión del jugador importa de verdad» | **Salen & Zimmerman** (§3) | ¿Es discernible (se ve que la causó él) e integrada (importa después)? |
| «El contenido nuevo no cuesta menos ni divierte más» | **Koster + Juul** (§2 + §9) | Comprueba si añade patrón nuevo (Koster) o solo baraja piezas ya vistas (progresión disfrazada) |

---

## 13 · Ejemplo aplicado: Luz de Ámbar por los nueve marcos

*Luz de Ámbar* es el plataformas de tres niveles que ya sirve de ejemplo completo en
[13 · 14 §6.3](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#63--ejemplo-real-un-plataformas-de-3-niveles):
una luciérnaga cruza tres ruinas antes de que se apague la última antorcha; un único salto sin
doble salto, muerte instantánea con respawn inmediato, y una luz visible que se agota como único
recurso. No se repite aquí el GDD completo — solo se pasa ese mismo diseño, ya congelado, por los
nueve marcos de este documento para mostrar que no son ejercicios abstractos.

| Marco | Lo que dice sobre *Luz de Ámbar* |
|---|---|
| **Koster** | El patrón que aprende el jugador es «leer el borde exacto de una plataforma bajo presión de tiempo». Con solo 3 niveles y sin doble salto, el patrón no llega a agotarse — si el juego creciera a 10 niveles, necesitaría una variación real del salto (no solo más pinchos) para seguir enseñando algo nuevo |
| **Salen & Zimmerman** | El respawn en menos de 0,5 s (P2 del GDD) es lo que mantiene cada muerte como jugada *discernible e integrada*: el jugador ve al instante qué la causó y vuelve a intentarlo con esa información, sin la fricción de una pantalla de carga que rompería el círculo mágico |
| **Schell — lentes** | La **Lente del Riesgo** aprobaría P3 (la luz visible que se agota): cada salto arriesgado tiene una consecuencia legible en pantalla, no un temporizador invisible. La **Lente de la Tétrada** señala que la mecánica (salto preciso) y la estética (tensión por la luz que se apaga) se refuerzan mutuamente — encajan |
| **SDT** | Autonomía baja a propósito (un único camino por nivel, sin rutas alternativas) — es una decisión válida para un arcade de 15 minutos, pero limita cuánto puede crecer el juego sin aburrir; competencia alta (el salto exige precisión real y se nota la mejora); relación no aplica — el propio GDD ya lo declara explícitamente («no hay bucle de meta») |
| **Bartle / Quantic Foundry** | Sirve casi en exclusiva al **triunfador** que persigue las gemas opcionales y, en menor medida, al jugador que busca dominar mecánicamente el salto (afín a `Mastery` de Quantic Foundry). No sirve a exploradores (niveles lineales, sin secretos que recompensen desviarse) ni a socializadores — coherente con el recorte explícito del GDD |
| **Costikyan** | El diseño no usa azar en absoluto: ni el salto, ni las trampas, ni el respawn dependen de un número aleatorio. Es una decisión correcta para un arcade de precisión — cualquier azar en el salto rompería la lectura exacta que pide P1 |
| **Dominancia estratégica** | Con un único verbo de salto y sin opciones equivalentes que elegir (no hay armas, no hay builds), no hay superficie donde pueda aparecer una estrategia dominante — el marco simplemente no aplica a este alcance, y está bien que no aplique |
| **Juul — emergencia/progresión** | Es un diseño de **progresión pura**: cada nivel presenta contenido de autor en un orden fijo (la hoja de nivel de `13 · 14 §6.3`, §8). No hay generación procedural ni sistemas que se crucen para producir variación — de nuevo, decisión correcta para 15 minutos de recorrido con presupuesto de un documento de ejemplo |
| **Fullerton** | Jugadores: 1. Objetivos: llegar a la antorcha final de cada nivel. Procedimientos: correr, saltar, agacharse. Reglas: R1-R4 de §5 del GDD. Recursos: la luz (único recurso visible). Conflicto: el tiempo antes de que se apague la última antorcha. Límites: cada nivel, de principio a fin. Resultado: variable, según cuántas gemas se recojan — las ocho casillas se rellenan sin dudar, señal de que el diseño estaba completo antes de programar nada |

Lo que este repaso deja claro es que **ningún marco obliga a añadir nada**: Costikyan y la
dominancia estratégica «no aplican» a este diseño concreto, y eso es información tan útil como
cuando sí aplican — confirma que el «§9 · Recorte explícito» del GDD citado en
[13 · 14 §6.3](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#63--ejemplo-real-un-plataformas-de-3-niveles)
(sin builds, sin azar, sin sistema social) es coherente con lo que el propio diseño necesita, no
una limitación que haya que disculpar.

---

## 14 · Checklist

- [ ] Puedes decir, para tu sistema principal, qué **patrón nuevo** aprende el jugador cada cierto
      tiempo, y en qué momento deja de haber uno nuevo que aprender (Koster).
- [ ] Sabes señalar una decisión de tu juego que sea *discernible e integrada*, y otra que no lo
      sea — y si la segunda debería serlo (Salen & Zimmerman).
- [ ] Elegiste 3-4 lentes de la tabla del §4.2 relevantes a tu género y las aplicaste por escrito
      al menos una vez sobre un sistema real (Schell).
- [ ] Para cada sistema de progresión o recompensa, anotaste qué necesidad de SDT sirve
      principalmente, y comprobaste que ninguna de las tres queda completamente a cero (SDT).
- [ ] Elegiste un tipo de jugador objetivo (Bartle o Quantic Foundry) y puedes nombrar a qué otro
      tipo renuncias a propósito (§6).
- [ ] Para cada elemento aleatorio, sabes si sirve a simulación, ruptura de simetría o nivelación
      — y comprobaste que hay suficientes tiradas para que la estrategia domine si eso es lo que
      quieres (Costikyan).
- [ ] Construiste, aunque sea a mano, la matriz de pagos de tu conjunto de opciones al mismo coste
      y buscaste si alguna fila domina a las demás (dominancia estratégica).
- [ ] Decidiste a propósito si cada sección de tu juego es de emergencia, de progresión, o una
      mezcla deliberada — y no por accidente de cómo salió el prototipo (Juul).
- [ ] Puedes rellenar las ocho casillas de elementos formales de tu juego, en una frase cada una,
      sin quedarte atascado en ninguna (Fullerton).
- [ ] Si un marco no aplica a tu alcance actual (como Costikyan y la dominancia no aplican a
      *Luz de Ámbar*), lo dejaste anotado como decisión consciente, no como un hueco sin revisar.

---

## 15 · Errores clásicos y cómo evitarlos

| Error | Por qué falla | Alternativa |
|---|---|---|
| Usar el test de Bartle para encasillar a una persona concreta | El propio Bartle avisa de que describe estereotipos de dinámica social en un MUD, no personalidades individuales | Úsalo para describir **mecánicas** («esto sirve al triunfador»), no personas |
| Tratar toda aleatoriedad como «mal diseño» | Ignora los tres usos legítimos del azar (simulación, ruptura de simetría, nivelación) que Costikyan documenta con ejemplos reales | Pregunta primero para qué está ahí el azar; si no hay respuesta, entonces sí es sospechoso |
| Nerfear la opción dominante bajándole el poder sin mirar el coste | Ataca el síntoma, no la causa: la próxima opción sobrevaluada al mismo coste ocupará su lugar | Ajusta el coste relativo primero (Schreiber, §8); el poder se toca cuando el coste ya no basta |
| Dar personalización cosmética y tratarla como si fuera una decisión mecánica | Rompe *meaningful play*: el jugador espera una consecuencia que nunca llega | Decide explícitamente si una elección es cosmética o mecánica, y comunícalo con claridad visual |
| Maximizar competencia (números, niveles) mientras la autonomía cae a cero | SDT predice un coste funcional que ningún refuerzo numérico compensa | Revisa las tres necesidades por separado; no asumas que una suple a las otras dos |
| Generar contenido procedural barajando piezas de autor y llamarlo «emergencia» | Es progresión con orden aleatorio: se agota igual de rápido que el contenido lineal, con el coste extra de parecer roto cuando la baraja produce una combinación rara | Diseña reglas que interactúen entre sí de verdad, o acepta que es progresión y trátala como tal |
| Aplicar las 18 lentes de §4.2 una por una sobre todo el juego | Es un ejercicio interminable que nadie termina, y por eso nadie lo hace la segunda vez | Elige 3-4 lentes relevantes al problema concreto que tienes delante, no al catálogo entero |
| Dar por hecho que un marco tiene que aplicar a todo diseño | Un plataformas de 15 minutos sin builds ni azar no tiene nada que decir sobre dominancia estratégica, y forzarlo inventa un problema que no existe | Comprueba si el marco aplica antes de usarlo; que no aplique es información válida (§13) |

---

## Ver también

- [13 · 01 — Diseño de juego](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) —
  MDA y Flow, que este documento enlaza en vez de repetir; el bucle de aprendizaje de Cook que
  conecta con Koster (§2); la regla de decisiones interesantes que Salen & Zimmerman enmarca (§3);
  la tabla de diagnóstico y la fila de dominancia que el §8 desarrolla con método
- [13 · 14 — El documento de diseño](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md) —
  el GDD de *Luz de Ámbar* que el §13 recorre con los nueve marcos, y las plantillas donde se
  puede insertar el campo «Necesidad SDT que sirve» o «Lentes aplicadas» de este documento
- [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](./16%20-%20Progresión%20-%20árboles%20de%20habilidades%2C%20desbloqueos%20y%20meta-progresión.md) —
  usa SDT (§5) y dominancia (§8) de forma directa: qué nodo «cambia cómo juegas» frente a un nodo
  de +5 %, y cuánta autonomía queda si el árbol tiene una única rama óptima
- [13 · 02 — Diseño de niveles](./02%20-%20Diseño%20de%20niveles.md) —
  Kishōtenketsu y los diez principios de Dan Taylor son, en el vocabulario de este documento,
  progresión de autor (Juul, §9) aplicada a la escala de una sala
- [13 · 12 — Diseño narrativo y diálogos](./12%20-%20Diseño%20narrativo%20y%20diálogos.md) —
  la ludonarrativa y las elecciones que importan frente a la ilusión de elección son
  *meaningful play* (§3) aplicado a la rama de diálogo
- [13 · 07 — Generación procedural avanzada](./07%20-%20Generación%20procedural%20avanzada.md) —
  donde se programa la emergencia (§9) que aquí solo se nombra: ruido, autómatas celulares,
  Wave Function Collapse
- [13 · 13 — Matemáticas aplicadas al juego](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
  la bolsa aleatoria y el crítico con piedad de §5 son ejemplos ya implementados del azar «que
  afecta a todos por igual» de Costikyan (§7)
- [13 · 11 — Producción, alcance y lanzamiento](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) —
  qué hacer cuando un marco revela que el alcance actual no puede sostener las nueve preguntas a
  la vez: se recorta el alcance, no las preguntas
- [04 · 05 — Roguelike y generación procedural](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) —
  el ejemplo de §6.3 y §9 (sirve a exploradores/triunfadores; mezcla emergencia y progresión)
- [04 · 06 — Metroidvania](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) —
  el género que casi siempre falla en autonomía (SDT, §5) si el gating deja una única ruta posible
- [_indice/auditorias/diseno-gdd.md](../_indice/auditorias/diseno-gdd.md) —
  la auditoría que encarga este documento (propuesta 2) y señala los huecos de negocio y
  monetización que siguen sin cubrir
- [RUTA.md](../RUTA.md) — este documento es material de nivel 3 en adelante, igual que `13 · 01`

---

## Fuentes

Todas consultadas el **2026-09-06**. `WebSearch` no se usó en ningún momento (agotado en esta
sesión, por indicación del encargo); todo lo de abajo se abrió con `curl -sL -A "Mozilla/5.0"` o
con la herramienta de lectura de páginas web, verificando código de respuesta y contenido real.

**Verificadas en vivo, contenido leído**

- Richard Bartle — *Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs* —
  <https://mud.co.uk/richard/hcds.htm> (HTTP 200) · los cuatro tipos, el eje actuar/interactuar
  y mundo/jugadores, y las tres advertencias literales del autor sobre los límites del modelo (§6)
- Jesper Juul — diccionario de *Half-Real* — <https://www.half-real.net/dictionary/> (HTTP 200) ·
  definiciones textuales de *emergence* y *progression* (§9)
- Jesper Juul — *The Open and the Closed: Games of Emergence and Games of Progression* —
  <https://www.jesperjuul.net/text/openandtheclosed.html> (HTTP 200) · la distinción completa con
  ejemplos (Ajedrez/*Counter-Strike* frente a aventuras gráficas) y el argumento de coste de
  contenido y rejugabilidad (§9)
- Greg Costikyan — *Randomness: Blight or Bane?*, charla de GDC Austin 2009 —
  <http://www.costik.com/randomness-blight-or-bane.htm> (HTTP 200) · la falsa dicotomía
  habilidad/azar, la regresión a la media, Póker como «estrategia como epifenómeno del azar», los
  tres usos deliberados del azar y las dos técnicas para evitar que decida la partida (§7)
- Greg Costikyan — *I Have No Words & I Must Design*, versión de 2002 —
  <http://www.costik.com/nowords2002.pdf> (HTTP 200, PDF de 25 páginas leído completo) · la
  definición de juego como «estructura interactiva de significado endógeno que exige a los
  jugadores luchar por un objetivo» y la taxonomía de ocho placeres de LeBlanc, contexto histórico
  de MDA ya cubierto en `13 · 01`; no se repite aquí por no aportar nada nuevo a este documento
- Ian Schreiber — *Level 3: Transitive Mechanics and Cost Curves*, blog *Game Balance Concepts* —
  <https://gamebalanceconcepts.wordpress.com/2010/07/21/level-3-transitive-mechanics-and-cost-curves/>
  (HTTP 200) · la definición de mecánica transitiva y la solución por curvas de coste (§8)
- Ian Schreiber — *Level 9: Intransitive Mechanics*, blog *Game Balance Concepts* —
  <https://gamebalanceconcepts.wordpress.com/2010/09/01/level-9-intransitive-mechanics/>
  (HTTP 200) · mecánicas intransitivas, estrategia dominante, matriz de pagos y eliminación
  iterativa (§8)
- Jesse Schell — página oficial de *The Art of Game Design* —
  <https://schellgames.com/art-of-game-design> (HTTP 200) · la definición de «lente» como
  *«cognitive framework»*, «over 100 distinct perspective filters», y las lentes de Comunidad,
  Reto, Economía y Riesgo citadas en el §4.2 (verificadas dos veces, con dos preguntas distintas)
- Self-Determination Theory — página oficial de la teoría —
  <https://selfdeterminationtheory.org/theory/> (HTTP 200) · la definición de las tres necesidades
  básicas (autonomía, competencia, relación) con cita textual (§5)
- Immersyve — <https://immersyve.com/> (HTTP 200) · confirma la filiación de Deci y Ryan con la
  empresa y su enfoque en satisfacción de necesidades básicas; no desarrolla el modelo PENS con
  detalle suficiente para citarlo con precisión (§5, marcado con ⚠️)
- *Rules of Play*, artículo de Wikipedia — <https://en.wikipedia.org/wiki/Rules_of_Play>
  (HTTP 200) · confirma la estructura en cuatro unidades del libro (*Core Concepts*, *Rules*,
  *Play*, *Culture*), que *meaningful play* es *«the goal of successful game design»*, la
  definición del círculo mágico y la mención de la actitud lúdica (§3); fuente terciaria, usada
  porque `mitpress.mit.edu` bloqueó el acceso (HTTP 403)
- *A Theory of Fun for Game Design*, artículo de Wikipedia —
  <https://en.wikipedia.org/wiki/A_Theory_of_Fun_for_Game_Design> (HTTP 200) · confirma solo la
  autoría del libro, no su tesis (§2, marcado con ⚠️)
- Tracy Fullerton / *Game Design Workshop* — <https://tracyfullerton.com/> (HTTP 200) y
  `gamedesignworkshop.com` vía instantánea de `web.archive.org` (HTTP 200) · el eslogan
  *«a playcentric approach to creating innovative games»* y *«the formal and dramatic systems of
  game design»*, citados literalmente (§10)

**No abiertas — bloqueadas o inaccesibles esta sesión, marcadas con ⚠️ en el texto y sin URL de cita**

- `quanticfoundry.com` — HTTP 403 en todos los intentos (bloqueo de tráfico automatizado, ya
  reportado por `_indice/auditorias/diseno-gdd.md`). Los 6 clústeres / 12 motivaciones del §6.2
  proceden del conocimiento general del campo, no de una lectura en vivo
- `mitpress.mit.edu` — HTTP 403 en la ficha de *Rules of Play*
- `raphkoster.com` — respondió HTTP 200 a una comprobación de cabecera pero no sirvió contenido
  en los reintentos posteriores (posible limitación de tráfico automatizado); `theoryoffun.com`
  devolvió HTTP 406
- Una URL de Mark Rosewater sobre «*input randomness*» / «*output randomness*» — no se pudo
  verificar; la distinción se presenta en el §7.1 con la terminología sí verificada de Costikyan
  (romper simetría al empezar frente a resolver una acción durante la partida)
- El texto completo de *A Theory of Fun for Game Design* (Koster) y de *Rules of Play* (Salen &
  Zimmerman) — ninguno de los dos libros tiene una edición completa accesible sin coste que esta
  sesión pudiera abrir; todo lo atribuido a ellos más allá de las citas textuales de arriba se
  marca con ⚠️ en el cuerpo del documento

**GameMaker**

- Símbolos de GML del §11 verificados con `python3 "_indice/buscar.py" <símbolo>` contra el
  `GmlSpec.xml` del runtime **2026.0.0.23**: `struct_exists`, `struct_get`, `struct_set`,
  `struct_get_names`, `array_length`, `show_debug_message`, `round`, `string` — todos de la
  familia *Variable Functions* y *Debugging*, ninguno obsoleto
