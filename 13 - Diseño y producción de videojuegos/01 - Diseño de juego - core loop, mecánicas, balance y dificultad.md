# 01 · Diseño de juego — core loop, mecánicas, balance y dificultad

> **La disciplina que decide si el juego merece existir, aplicada a un desarrollo con
> GameMaker.** Este documento no enseña a programar: enseña a **decidir qué programar**, a
> **medir si funciona** y a **dejarlo escrito** de forma que otra persona —o un LLM— pueda
> continuarlo sin adivinar.
>
> **Qué NO cubre.** El *feedback* audiovisual del golpe (screen shake, hit stop, tweens) está
> en [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md).
> El montaje del juego completo (splash, menú, pausa, créditos) está en
> [04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md).
> Las herramientas del Debug Overlay y el `profiler` están en
> [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md);
> aquí se usan, no se explican de cero. Y la implementación concreta de cada género vive en
> [04 · Recetas por género](../04%20-%20Recetas%20por%20género/_INDICE-RECETAS.md).

---

## ⚠️ Aviso de vocabulario: «core loop» significa dos cosas en esta biblioteca

| Dónde | Qué significa |
|---|---|
| En las recetas de género (`04/*`, sección 3 de cada una) | El **orden de ejecución por fotograma**: qué hace `Begin Step`, qué hace `Step`, qué hace `Draw`. Es una decisión de arquitectura. |
| En este documento | El **bucle de decisiones del jugador**: qué hace, qué recibe a cambio y por qué vuelve a hacerlo. Es una decisión de diseño. |

Los dos son reales y los dos importan. Cuando un documento diga «core loop», mira si habla de
*frames* o de *jugador*. Aquí siempre habla del jugador.

---

## 1 · Los principios

### 1.1 · Qué es un juego, en términos operativos

Un juego es un conjunto de **reglas** que limitan unos **verbos**, apuntados a un **objetivo**,
con **feedback** suficiente para que el jugador construya un modelo mental de cómo funciona
todo eso. Las cuatro piezas:

| Pieza | Pregunta que responde | Si falta |
|---|---|---|
| **Verbos** | ¿Qué puede *hacer* el jugador? | No hay juego: hay una película |
| **Reglas** | ¿Qué limita esos verbos? ¿Qué los hace costosos? | No hay decisión: todo funciona siempre |
| **Objetivos** | ¿Hacia dónde apuntan? | No hay dirección: el jugador deambula |
| **Feedback** | ¿Cómo sabe el jugador qué acaba de pasar? | No hay aprendizaje: el juego parece aleatorio |

**El diseño empieza por los verbos, y son menos de los que crees.** Escribe la lista de verbos
de tu juego. Si pasan de cinco y no eres un estudio de cincuenta personas, el proyecto ya está
en problemas.

```
Celeste              → correr · saltar · agarrarse · dash                      (4)
Tetris               → mover · rotar · acelerar la caída                       (3)
Vampire Survivors    → moverse · elegir mejora                                 (2)
Papers, Please       → mirar · comparar · sellar                               (3)
```

Cada uno de esos juegos tiene decenas de sistemas encima. Pero los verbos —lo que los dedos
hacen— son cuatro o menos. Los verbos son el presupuesto más caro del diseño: cada verbo nuevo
hay que enseñarlo, hay que darle *feedback*, hay que balancearlo y hay que cruzarlo con todos
los demás.

### 1.2 · El bucle de aprendizaje: por qué el jugador vuelve

Cada interacción del jugador recorre cuatro pasos:

```
   ┌──────────────────────────────────────────────────────────┐
   │  1. ACCIÓN        el jugador hace algo (un verbo)         │
   │  2. SIMULACIÓN    el juego aplica sus reglas              │
   │  3. FEEDBACK      el juego devuelve el resultado          │
   │  4. MODELO        el jugador entiende un poco mejor       │
   └───────────────────┬──────────────────────────────────────┘
                       └──► vuelve a 1, ahora con mejor criterio
```

Es el bucle de Daniel Cook (*Loops and Arcs*). La conclusión operativa es dura y muy útil:

> **Un bucle en el que el paso 4 no ocurre no es un juego: es una tarea.** Si tras cien
> repeticiones el jugador no entiende nada nuevo ni juega mejor, has construido una noria.

Corolario: **el feedback no es adorno, es el canal por el que el jugador aprende.** Por eso
[15 · Game feel](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) es una
receta de diseño, no de decoración.

Cook distingue además el **bucle** (se repite y mejora el modelo) del **arco** (se consume una
sola vez: una escena, un giro de guion, un jefe único). Los arcos son caros por minuto de
juego; los bucles son baratos. Un juego que solo tiene arcos necesita un equipo grande.

### 1.3 · MDA: mecánica → dinámica → estética

MDA (Hunicke, LeBlanc y Zubek, 2004) parte de una observación incómoda: **el diseñador y el
jugador miran el mismo sistema desde extremos opuestos.**

```
   DISEÑADOR  ──►  Mechanics  ──►  Dynamics  ──►  Aesthetics  ◄──  JUGADOR
                   (reglas y      (lo que      (lo que el
                    datos)         emerge)      jugador siente)
```

| Capa | Definición del paper | En tu proyecto |
|---|---|---|
| **Mechanics** | Los componentes del juego al nivel de representación de datos y algoritmos | Tu GML, tus tablas, tus constantes |
| **Dynamics** | El comportamiento en tiempo de ejecución de las mecánicas actuando sobre la entrada del jugador y sobre las salidas de las demás, a lo largo del tiempo | «Los jugadores acaparan munición», «todos eligen la misma arma» |
| **Aesthetics** | Las respuestas emocionales deseables que se evocan en el jugador cuando interactúa con el sistema | «Es tenso», «se hace repetitivo», «es injusto» |

El paper propone además una taxonomía de **ocho tipos de diversión** para dejar de decir
«divertido», que no significa nada:

**Sensation** (placer sensorial) · **Fantasy** (hacer creer) · **Narrative** (drama) ·
**Challenge** (carrera de obstáculos) · **Fellowship** (marco social) · **Discovery**
(territorio inexplorado) · **Expression** (descubrirse a uno mismo) · **Submission**
(pasatiempo). El propio paper etiqueta así sus ejemplos: *Charades* = Fellowship + Expression +
Challenge; *Quake* = Challenge + Sensation + Competition + Fantasy.

**Para qué sirve de verdad esta lista:** escribe cuáles son las **dos** estéticas que tu juego
persigue, en orden. Cuando dudes entre dos diseños, gana el que sirva a la primera. Un juego
que persigue las ocho no persigue ninguna.

### 1.4 · Usar MDA para diagnosticar un prototipo

Aquí está el valor práctico del modelo: **una estética no se puede depurar directamente.** No
existe la línea de código «hazlo menos aburrido». Lo que se hace es bajar de capa:

```
   síntoma (estética)  →  ¿qué dinámica lo produce?  →  ¿qué mecánica genera esa dinámica?
                                                          └─► ahí está la palanca
```

| Síntoma que oyes en el playtest | Dinámica sospechosa | Mecánica que la produce | Palanca típica |
|---|---|---|---|
| «Se hace repetitivo» | Una sola estrategia domina | El coste de la opción dominante no crece | Coste creciente, munición limitada, enfriamiento |
| «No sé qué hacer» | El jugador no tiene objetivo legible | El objetivo no está en pantalla ni en el nivel | Señalización, brújula, encuadre del nivel |
| «Es injusto» | Muerte sin aviso previo | Telegrafiado demasiado corto o fuera de cámara | Anticipación, sonido de aviso, zona de seguridad |
| «Aburre a los diez minutos» | El bucle no cambia nunca | Un solo sistema, sin nada que lo modifique | Un segundo sistema que altere el primero |
| «Gano sin esforzarme» | Realimentación positiva sin freno | La recompensa es proporcional al poder actual | Sumidero, coste creciente, escalado de enemigos |
| «Todos eligen lo mismo» | Una opción domina en todo contexto | Las opciones no tienen contextos donde ganar | Dar a cada opción un contexto propio |
| «No me entero de si voy ganando» | El estado del sistema es invisible | No hay lectura del estado en pantalla | HUD, cambio visual del mundo, sonido |

> 💡 **La pregunta de oro en un playtest no es «¿te ha gustado?», es «¿qué estabas intentando
> hacer ahí?».** La primera te da una estética sin dinámica; la segunda te da la dinámica, que
> es lo que puedes tocar.

### 1.5 · Mecánicas frente a sistemas

| | **Mecánica** | **Sistema** |
|---|---|---|
| Qué es | Una regla | Un conjunto de reglas **con estado propio** que evoluciona |
| Ejemplo | «Saltar sobre un enemigo lo mata» | La economía, el clima, la reputación, el hambre |
| Coste de añadirlo | Bajo | Alto: hay que enseñarlo, mostrarlo y balancearlo |
| Qué aporta | Una acción más | **Situaciones nuevas al cruzarse con otros sistemas** |

**La regla del segundo sistema.** Un sistema solo suele valer su coste si **modifica a otro
que ya existe**. Un sistema de clima que solo cambia el color del cielo es decoración cara. El
mismo sistema de clima, si la lluvia moja el suelo y el suelo mojado conduce la electricidad y
el rayo prende la hierba seca, es diseño.

### 1.6 · Diseño elegante: pocas reglas, muchas situaciones

La medida práctica de la elegancia es un cociente:

```
        situaciones distintas que el jugador reconoce
  E  =  ─────────────────────────────────────────────
                   reglas que hay que enseñar
```

Cuatro reglas bien cruzadas dan doce situaciones. Doce reglas sueltas dan doce situaciones y
cuestan tres veces más de enseñar, de programar y de balancear. Ejemplo con cuatro elementos:

| ↓ actúa sobre → | **Fuego** | **Agua** | **Electricidad** | **Viento** |
|---|---|---|---|---|
| **Fuego** | — | evapora, crea vapor | — | se propaga y crece |
| **Agua** | apaga | — | conduce a lo mojado | forma olas, empuja |
| **Electricidad** | prende lo seco | se dispersa al conducirse | — | — |
| **Viento** | aviva y desplaza | mueve la superficie | — | — |

Cada celda con contenido es una situación que el jugador puede **descubrir sin que se la
expliques**. Ese descubrimiento es la estética *Discovery* de MDA, y sale gratis: no hay que
crear contenido, solo que las reglas se hablen entre sí.

Tynan Sylvester define la elegancia exactamente así en *Designing Games*: «maximizar el poder
emocional y la variedad de las experiencias de juego minimizando la carga de comprensión del
jugador y el esfuerzo del desarrollador». Y da tres olfatos para reconocerla mientras diseñas:

- **Huele a elegancia** una mecánica que **interactúa con muchas otras**.
- **Huele a elegancia** una mecánica **simple**.
- **Huele a elegancia** una mecánica que **se reutiliza mucho**.

Lo contrario —la mecánica que solo se usa en un sitio, no toca a nada y hay que explicar— es
contenido disfrazado de sistema. Sylvester llama **emergencia** a lo que produce la elegancia:
«cuando mecánicas simples interactúan para crear situaciones complejas».

> 🔺 **El precio de la elegancia es la disciplina para decir que no.** Cada regla nueva hay que
> cruzarla con todas las anteriores: la matriz crece al cuadrado. Con cinco sistemas hay diez
> parejas que revisar; con diez sistemas, cuarenta y cinco. Por eso los juegos elegantes tienen
> pocos sistemas, no muchos.

---

## 2 · El core loop y los bucles anidados

### 2.1 · Los tres relojes

Un juego que aguanta tiene tres bucles encajados, y cada uno alimenta al siguiente:

| Bucle | Escala | Ejemplo | Qué vive ahí | Qué entrega al de abajo |
|---|---|---|---|---|
| **Acción** | segundos | apuntar → disparar → esquivar | El *game feel* | Recursos, daño, progreso de sala |
| **Sesión** | 5-40 min | sala → recompensa → mejora → sala más dura | La curva de dificultad | Desbloqueos, historia, maestría |
| **Meta** | horas | desbloquear arma → cambia cómo juegas | La razón de volver mañana | — |

**Las dos reglas que valen por todo el resto:**

1. **Cada bucle debe cambiar el de arriba.** Si la mejora que ganas en el bucle de sesión no
   cambia lo que haces en el bucle de acción, la mejora es un número, no una decisión.
2. **Un bucle sin el siguiente se agota.** Solo con bucle de acción tienes una demo de tres
   minutos. Con acción y sesión tienes un juego de jam. Los tres son un juego que se publica.

Un juego pequeño puede tener dos bucles y estar terminado. Puede no tener el de meta a
propósito (un arcade puro). Lo que no puede es **creer** que lo tiene.

### 2.2 · Dibujarlo antes de programar

La prueba de que existe un bucle es que **cabe en una frase con tres huecos**:

```
El jugador ______ para conseguir ______, que le permite ______ mejor.
```

Si no puedes rellenar los tres huecos, no hay bucle: hay una lista de características.

```
Ejemplos rellenados
───────────────────
Vampire Survivors:  esquiva  →  para conseguir gemas de experiencia
                             →  que le permiten elegir armas que matan solas.
Slay the Spire:     gana combates  →  para conseguir cartas y reliquias
                                   →  que le permiten construir un motor de turno.
Un tower defense:   mata oleadas  →  para conseguir oro
                                  →  que le permite poner torres que matan mejor.
```

**La plantilla del bucle, en cinco casillas.** Cópiala al GDD y rellénala antes de escribir
una línea de GML:

```
[1] ACCIÓN     ¿qué verbo se repite, y cuántas veces por minuto?
[2] RIESGO     ¿qué puede salir mal? ¿qué se pierde?
[3] RECOMPENSA ¿qué gana: recurso, información o poder?
[4] DECISIÓN   ¿en qué lo gasta? ¿hay más de una opción buena?
[5] CAMBIO     ¿qué hace ahora [1] distinto de antes?  ──► vuelve a [1]
```

Si la casilla **[5] está vacía, el bucle no gira**: el jugador repite lo mismo indefinidamente.
Si la **[4] tiene una sola opción**, no hay decisión: es un peaje, no un bucle.

### 2.3 · Probarlo sin motor

Antes de abrir GameMaker, el bucle se prueba de tres maneras, en este orden y en menos de un
día entero:

| Prueba | Cómo | Qué detecta |
|---|---|---|
| **De frase** | Rellenar los tres huecos de arriba | Que no hay bucle en absoluto |
| **De papel** | Jugar diez turnos con dados, fichas y un folio | Que la decisión [4] es falsa (siempre gana la misma opción) |
| **De hoja de cálculo** | Simular 100 iteraciones de la economía en columnas | Que la economía se rompe (inflación, muro, bola de nieve) |

La prueba de papel es especialmente barata en juegos de gestión, cartas, roguelikes y tower
defense. En un juego de acción no sirve para el bucle de acción (que es puro control), pero
sí sirve para el de sesión y el de meta, que son los que suelen estar mal.

> 💡 **Regla de decisión:** una decisión es interesante cuando **cada opción es la mejor en
> algún contexto** y el jugador no sabe con certeza en cuál está. Si una opción gana siempre,
> bórrala y quédate con ella. Si ninguna gana nunca, bórralas todas.

---

## 3 · Progresión y curva de dificultad

### 3.1 · Flow: la banda entre el aburrimiento y la ansiedad

El marco que usa todo el oficio viene de Csikszentmihalyi y llegó al diseño de videojuegos por
la tesis de Jenova Chen, *Flow in Games* (2006). La formulación que interesa:

> Para mantener la experiencia de *flow*, la actividad tiene que **equilibrar el reto con la
> habilidad** del participante. Si el reto supera a la habilidad, la actividad abruma y genera
> **ansiedad**. Si el reto queda por debajo, provoca **aburrimiento**.

```
  reto ▲                          ANSIEDAD → «es injusto», abandona
       │                 ╱╱╱╱╱
       │           ╱╱╱╱╱  ← banda de flow
       │     ╱╱╱╱╱      ABURRIMIENTO → «es repetitivo», abandona
       └──────────────────────────────► habilidad del jugador
```

Las dos consecuencias que se olvidan siempre:

1. **La habilidad del jugador crece durante la propia sesión.** Una dificultad constante se
   convierte en aburrimiento sin que toques nada.
2. **La banda es distinta para cada persona y bastante estrecha.** Una sola curva no puede
   servir a todo el mundo. De ahí las dos soluciones de §3.3.

Jesse Schell empaqueta esto como la **lente del Flow**, y sus preguntas son un buen chequeo
rápido de cualquier nivel: *¿tiene mi juego objetivos claros?* y *¿ofrece un flujo constante de
retos ni demasiado fáciles ni demasiado difíciles?*

### 3.2 · Las cuatro formas de curva

| Forma | Cómo es | Cuándo usarla | Riesgo |
|---|---|---|---|
| **Rampa** | Sube monótonamente | Arcades y juegos por puntuación | Se aclimata: el jugador deja de notar el cambio |
| **Dientes de sierra** | Sube, **cae** al dar una herramienta nueva, vuelve a subir más alto | **La forma por defecto de un juego con progresión** | Si el diente no baja lo suficiente, la herramienta nueva no se siente poderosa |
| **Escalones** | Meseta larga + salto | Juegos por zonas o mundos | La meseta aburre si no enseña algo |
| **Pico y valle** | Jefe (pico) seguido de descanso deliberado (valle) | Cualquier juego con jefes | Sin valle, el siguiente pico no se siente alto |

En los dientes de sierra, la caída no es un regalo: es **el momento en que el jugador se siente
poderoso**. Un juego que solo sube nunca da esa sensación. Y cada pico posterior debe quedar
**por encima** del anterior, o la progresión se percibe plana.

**La regla del 3 + 1** para colocar los encuentros dentro de un diente:

```
  encuentro 1 → presentar la mecánica en un sitio donde fallar no cuesta
  encuentro 2 → ampliarla (más rápido, más lejos, más de lo mismo)
  encuentro 3 → combinarla con algo que el jugador ya domina
  encuentro 4 → EXAMEN: exige dominarla, y fallar cuesta
```

Es la misma estructura que §5 usa para el *onboarding*, porque **enseñar y subir la dificultad
son la misma operación vista desde dos lados**.

### 3.3 · Dificultad dinámica: las dos familias, y cuál elegir

| | **DDA oculta** | **Asistencia explícita** |
|---|---|---|
| Qué hace | El juego ajusta sin decirlo | El jugador elige y lo sabe |
| Ejemplos | *Rubber banding* en carreras, directores que reparten munición | Modo asistido, escalas de dificultad, opciones sueltas |
| Ventaja | No rompe la ficción; nadie tiene que decidir nada | Honesta, accesible, no invalida el logro |
| Riesgo | **Si el jugador la nota, se siente estafado**: su victoria deja de ser suya | Requiere presentarla sin culpabilizar |

Chen ya advertía en 2006 de que **diseñar e implementar una DDA no es trivial** y de que muy
pocos desarrolladores comerciales habían llegado a publicar una. Sigue siendo cierto.

**La recomendación por defecto: asistencia explícita, y DDA solo donde el jugador no pueda
notarla.** Lo que se puede ajustar en silencio sin romper nada:

- El *drop* de munición y curación (no la vida del jefe).
- La agresividad del enemigo cuando está fuera de cámara.
- El tiempo de gracia tras un golpe (*i-frames*), en un margen pequeño.

Lo que **no** se ajusta en silencio: la vida de los enemigos, el daño que hacen y el tiempo
límite. Son las tres cosas que el jugador está midiendo activamente.

*Celeste* es el caso de referencia. Maddy Thorson admite que «desde mi perspectiva como
diseñadora del juego, el modo asistido **rompe** el juego», y aun así lo incluyeron buscando
«una experiencia fluida en la que los jugadores puedan moverse libremente entre niveles de
dificultad poco definidos, **sin juicio ni insinuación de que no están jugando "como se
pretendía"**». Se iba a llamar «Cheat Mode» y lo renombraron por ese matiz de juicio.

> 💡 **Traducción a decisiones concretas:** si añades asistencias, (a) hazlas granulares —
> velocidad del juego, invencibilidad, recursos infinitos, saltar capítulo— en vez de un
> «Fácil/Normal/Difícil»; (b) escribe el texto de la pantalla sin la palabra «trampa»; (c) no
> bloquees logros ni final por usarlas. Ver
> [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) y
> [04 · 25 — Menú de opciones y ajustes](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md).

### 3.4 · Medir la dificultad con datos, no con opiniones

Una curva de dificultad se dibuja a ojo y se corrige con números. **Los cuatro números que
pagan su coste** el primer día que los tienes:

| Métrica | Cómo se calcula | Qué te dice |
|---|---|---|
| **Muertes por sala** | Eventos `muerte` agrupados por `sala` | Dónde está el pico. Una sala con el 30 % de las muertes es un muro |
| **Tiempo mediano por sala** | Mediana de `salida - entrada` por sala | Dónde el jugador se atasca sin morir (peor: se aburre atascado) |
| **Embudo de progreso** | % de sesiones que llegan a cada sala | Dónde abandona la gente. El abandono manda sobre todo lo demás |
| **Intentos hasta superar** | Media de muertes en la sala antes de pasarla | Si es 1, la sala no enseña nada; si pasa de 8-10, frustra |

**Usa la mediana, no la media.** Un tester que se levanta a por café convierte una media de
40 s en una de 300 s. La mediana lo ignora.

> 🔺 **Un dato sin una pregunta previa es ruido.** Antes de registrar nada, escribe la pregunta:
> «¿la sala 7 mata más que la 6?». La telemetría contesta preguntas; no las inventa. El código
> completo, en [§9.5](#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json).

---

## 4 · Economía y balance

### 4.1 · El vocabulario correcto

Casi todo el balance de un juego es un problema de **flujo de recursos**. La terminología
estándar viene de *Game Mechanics: Advanced Game Design* (Adams y Dormans, 2012), el libro que
originó la herramienta Machinations:

| Pieza | Definición del libro | En un juego tuyo |
|---|---|---|
| **Pool** | Donde se acumula un recurso | `global.oro`, la vida del jugador, el inventario |
| **Fuente** (*source*) | Mecánica que **crea recursos de la nada** al cumplirse una condición | El enemigo suelta oro; el maná se regenera; el tiempo pasa |
| **Sumidero** (*drain*) | Lo contrario: **saca recursos del juego de forma permanente** | Comprar, gastar munición, recibir daño, reparar |
| **Convertidor** (*converter*) | Transforma un recurso **en otro** | Crafteo, fundición, comprar objetos con oro |
| **Intercambiador** (*trader*) | Mueve recursos entre entidades según una regla de cambio. **No crea ni destruye nada** | Comercio entre jugadores, trueque con un NPC |

> 🔺 **Convertidor ≠ intercambiador.** El convertidor destruye una cosa y crea otra (el árbol
> desaparece, aparece madera). El intercambiador solo cambia de manos lo que ya existía. Si los
> confundes en la hoja de cálculo, tu economía tendrá una fuente oculta y no sabrás por qué se
> infla.

### 4.2 · Realimentación: por qué las partidas se deciden pronto o no acaban nunca

| | **Positiva** | **Negativa** |
|---|---|---|
| Qué hace | El éxito genera más éxito | El éxito genera más resistencia |
| Efecto | **Bola de nieve**: la partida se decide antes de terminar | **Estabiliza**: la partida no se acaba nunca |
| Ejemplo clásico | El líder del Monopoly cobra más y compra más | El termostato; el escalado de precios |
| Herramienta en tu juego | Interés compuesto, mejoras que se potencian | Coste creciente, escalado por nivel, *rubber banding* |

El propio paper de MDA usa esos dos ejemplos —el termostato y el enriquecimiento del líder en
Monopoly— para explicar por qué la realimentación positiva sin freno **destruye la tensión
dramática**: cuando el resultado ya se sabe, lo que queda de partida sobra.

**La receta:** un juego necesita las dos. La positiva es la que da la sensación de poder (el
bucle de meta de §2.1 casi siempre es positivo). La negativa es la que mantiene la partida viva.
El diseño consiste en **acotar la positiva** con un sumidero o un techo, no en eliminarla.

### 4.3 · La regla que evita el 80 % de los desastres de economía

> **Todo recurso necesita un sumidero.** Si un recurso solo entra y nunca sale, se infla; al
> inflarse deja de significar nada; y cuando deja de significar nada, todas las decisiones que
> dependían de él desaparecen.

**Cómo detectar la inflación sin herramientas caras:** registra `oro_en_el_bolsillo` cada
minuto en un playtest y píntalo. Tres formas y lo que significan:

| Forma | Diagnóstico |
|---|---|
| **Sube y baja** `▁▄▂▆▃▇▄█▅` | Economía viva: el jugador gasta lo que gana |
| **Sube sin parar** `▁▂▃▄▅▆▇█` | **Inflación**: los precios dejaron de importar y comprar ya no es una decisión |
| **Plano en cero** `▁▁▁▁▁▁▁▁` | **Muro**: nunca puede comprar; la casilla [4] del bucle no existe |

Si sale **B**, no subas los precios: **añade o abarata un sumidero**. Subir los precios solo
retrasa la inflación un rato.

### 4.4 · Balance por fórmulas, con números

Balancear a mano cincuenta objetos no escala. Se fija **una fórmula** y se ajustan dos o tres
parámetros; las excepciones se marcan a mano y se cuentan (si hay más de un 10 % de
excepciones, la fórmula está mal).

#### Curva de coste geométrica

```
  coste(n) = coste_base × razón ^ n
```

Con `coste_base = 25` y `razón = 1,18`:

| Nivel n | Coste | Coste acumulado |
|---|---|---|
| 0 | 25 | 25 |
| 1 | 30 | 55 |
| 2 | 35 | 90 |
| 5 | 57 | 249 |
| 10 | 131 | 826 |
| 20 | 684 | 4 806 |

La propiedad que hay que entender: **la razón fija cada cuántos niveles se duplica el coste.**

| Razón | Se duplica cada… | Sensación |
|---|---|---|
| 1,07 | 10 niveles | Progresión larga, tipo RPG de 40 horas |
| 1,15 | 5 niveles | El estándar de los juegos de mejora |
| 1,18 | 4 niveles | Notas el freno enseguida |
| 1,35 | 2,3 niveles | Muro rápido: para máximo 5 o 6 niveles |

Y la regla que empareja coste con ingreso: **si tu producción también crece de forma
geométrica con razón `p`, el tiempo hasta la siguiente compra es constante cuando `razón = p`.**
Si `razón > p`, cada nivel tarda más (el juego se frena, que suele ser lo que quieres). Si
`razón < p`, cada nivel tarda menos y el juego se descontrola en veinte minutos.

#### Daño frente a vida: el TTK (*time to kill*)

```
  golpes  = ceil(vida_enemigo / daño_por_golpe)
  TTK (s) = (golpes − 1) × (cadencia_en_frames / fps)
```

El `− 1` está a propósito: el primer golpe ocurre en el instante 0.

Ejemplo con una pistola de `daño 15` y `cadencia 12 frames` a 60 fps (5 disparos por segundo):

| Enemigo | Vida | Golpes | TTK | Lectura |
|---|---|---|---|---|
| Baba | 30 | 2 | 0,20 s | Trivial: carne de cañón, sirve para el ritmo |
| Arquero | 45 | 3 | 0,40 s | Rápido: el peligro está en su daño, no en su vida |
| Bruto | 180 | 12 | 2,20 s | Es un obstáculo: el jugador tendrá que moverse mientras dispara |
| Jefe | 3 000 | 200 | 39,8 s | Combate largo: **necesita fases**, o se hace tedioso |

**Heurísticas de TTK** — ⚠️ son reglas de oficio contrastadas por uso, no cifras de una fuente
primaria; ajústalas a tu juego:

| Situación | TTK razonable |
|---|---|
| Enemigo básico en un juego de acción | 0,2 – 1 s |
| Enemigo de élite | 2 – 5 s |
| Jefe | 40 – 150 s, **repartidos en 2-4 fases** |
| El jugador muriendo (TTK inverso) | ≥ 3 golpes; menos de 3 sin aviso se percibe como injusto |

#### Balancear en múltiplos, no en absolutos

Fija una unidad —el **golpe estándar**— y expresa todo lo demás como múltiplos de ella:

```
  golpe estándar = 15 de daño
  pistola  = 1,0 × golpe   escopeta = 3,6 × golpe (6 perdigones de 0,6)
  baba     = 2   golpes    arquero  = 3 golpes    bruto = 12 golpes
```

Ahora, si el juego se siente lento, **cambias el golpe estándar** y todo el juego se reescala a
la vez sin tocar cincuenta números. Este es el motivo de fondo por el que los valores viven en
una tabla y no repartidos por el código.

### 4.5 · De la hoja de cálculo al juego

La hoja de cálculo es la herramienta correcta para 200 filas de contenido: ves la columna
entera, ordenas, comparas, pintas la curva y detectas el atípico de un vistazo. El pipeline:

```
  Hoja de cálculo  ──exportar──►  CSV / JSON  ──Included Files──►  struct en GML
    (la verdad)                   (el puente)                       (lo que corre)
        ▲                                                                │
        └──────────── el balance ajustado en caliente vuelve aquí ◄───────┘
```

**Reglas del pipeline que evitan sufrimiento:**

1. **La hoja manda.** Nadie edita el JSON a mano; se regenera. Si alguien lo edita, la próxima
   exportación borra su trabajo y nadie sabe por qué.
2. **Una columna `id` en primer lugar**, en `snake_case`, sin espacios ni tildes: es la clave
   del struct.
3. **Una fila = una entidad**, y nunca celdas combinadas: rompen cualquier exportación.
4. **Números puros**, sin separador de miles ni símbolo de moneda.
5. **Versión en la propia tabla** (`version: "1.4.0"`) y cotéjala al cargar: te ahorra el bug de
   «el juego usa un balance viejo» que se come una tarde entera.

El código de carga —CSV y JSON— está en [§9.3](#93--datos-de-balance-en-included-files).

---

## 5 · Onboarding: enseñar sin texto

### 5.1 · La regla de «una idea nueva cada vez»

**Nunca introduzcas dos mecánicas en la misma pantalla.** Si el jugador falla, no sabrá cuál de
las dos no entendió, y tú tampoco al ver la grabación. Una idea, un sitio, una prueba.

Para cada mecánica, las mismas cuatro fases de §3.2, ahora vistas como enseñanza:

| Fase | Qué hace el nivel | Coste del fallo |
|---|---|---|
| **1 · Presentar** | La mecánica es la **única** salida, en un sitio seguro | Cero |
| **2 · Ampliar** | Lo mismo, con más exigencia | Bajo |
| **3 · Combinar** | Con una mecánica ya dominada | Medio |
| **4 · Examinar** | Exige dominio | Alto: aquí se muere |

Ese esqueleto es lo que la crítica lleva quince años señalando en el nivel 1-1 de *Super Mario
Bros.*: presentar el salto, ampliarlo, combinarlo con el enemigo y examinarlo con la tubería.
⚠️ Es una lectura crítica ampliamente compartida —no una declaración de diseño publicada por
Nintendo—, pero funciona igual de bien como plantilla.

### 5.2 · Las cinco herramientas para enseñar con el nivel

| Herramienta | Cómo se aplica |
|---|---|
| **Encuadre** | Que lo importante sea lo único que se ve. Sitúa la cámara para que el objeto nuevo esté solo en pantalla |
| **Camino único** | Si la única salida exige la mecánica, el jugador la descubre sin que se lo digas |
| **Demostración segura** | Enséñale el peligro haciendo daño **a otro**: un enemigo que cae al pincho antes de que tú llegues |
| **Repetición con variación** | La misma idea tres veces, cada una un poco distinta: el patrón se hace consciente |
| **Recompensa por curiosidad** | Una moneda tras un salto difícil enseña la mecánica premiando la exploración, sin obligar |

### 5.3 · Gating: la mecánica no aparece hasta que la anterior está probada

*Gating* es controlar **qué existe** en el mundo según lo que el jugador ha demostrado. En
GameMaker se resuelve con un struct de progreso y un filtro al instanciar:

```gml
/// scr_progreso — el gating vive en datos, nunca en if repartidos por el código
function progreso_iniciar() {
    global.progreso = { dash: false, doble_salto: false, gancho: false };
}

/// @description ¿Se puede colocar esta pieza de contenido todavía?
/// @param {String} _requiere  Nombre de la habilidad exigida, o "" si no exige ninguna
function contenido_permitido(_requiere) {
    if (_requiere == "") return true;
    if (!struct_exists(global.progreso, _requiere)) return false;
    return struct_get(global.progreso, _requiere);
}

/// En el Create del generador de la sala
if (contenido_permitido("dash")) {
    instance_create_layer(x, y, "Instancias", obj_pasillo_de_dash);
}
```

> 💡 **Comprueba que el gating funciona al revés.** Un jugador que vuelve con el gancho a la
> primera zona debe encontrar algo. Si no, el mundo se siente muerto una vez desbloqueado todo.

### 5.4 · El examen de los primeros 60 segundos

Sin leer nada, el jugador debe poder responder: **quién soy · qué puedo hacer · adónde voy ·
qué me mata**. Si falla una, el minuto 1 está mal diseñado, y el minuto 1 es el que decide si
hay minuto 10.

---

## 6 · Prototipado rápido

### 6.1 · Qué se prototipa primero

**Lo que puede matar el proyecto.** El orden es: la incertidumbre más cara primero.

| Prototipa | No prototipes |
|---|---|
| La mecánica de la que depende todo lo demás | Menús, opciones, guardado, localización |
| El bucle de sesión completo, aunque sea feísimo | Arte, sonido y UI definitivos |
| El sistema que nadie ha hecho antes | Lo que ya sabes que funciona porque está en [las recetas](../04%20-%20Recetas%20por%20género/_INDICE-RECETAS.md) |

**Escribe la pregunta en la primera línea del archivo.** Literalmente:

```gml
// PROTOTIPO 03 — Pregunta: ¿es divertido invertir la gravedad a voluntad
//                mientras esquivas proyectiles?  Presupuesto: 1 día.
//                Respuesta (rellenar al terminar): ______
```

Un prototipo sin pregunta escrita se convierte en un juego a medias que nadie quiere tirar.

### 6.2 · Cajas grises

Rectángulos de colores por rol —el jugador de un color, lo que mata de otro, lo que se recoge
de un tercero— con `draw_rectangle` y punto. **El arte tapa los problemas de diseño**: si con
cajas es aburrido, con arte seguirá siéndolo, pero tardarás tres meses más en darte cuenta y
tendrás demasiado invertido para tirarlo.

El equipo de *Dyo* lo llevó un paso más allá y prototipó **sin ordenador**: «antes de empezar a
programar hicimos prototipado analógico… usamos bloques de madera de juguete para bocetar
rápidamente algunas estructuras básicas de nivel».

### 6.3 · Cuándo tirar el prototipo

**Siempre.** El prototipo responde una pregunta y se borra: su código está escrito para ir
rápido, no para durar, y refactorizarlo cuesta más que reescribirlo sabiendo ya la respuesta. Lo
que sobrevive es **la respuesta**, escrita en el GDD. Tres criterios de parada, fijados antes de
empezar: **presupuesto agotado** (si diste un día y no hay respuesta, la respuesta es no);
**tres prototipos sin encontrar la gracia** (el problema es la premisa, no la ejecución);
**contestado antes de tiempo** (si a las dos horas ya sabes que sí, para — seguir es empezar el
juego dentro del prototipo).

> 💡 Un caso real del blog oficial: en el retorno de BancyCo a GameMaker, el autor cuenta que
> hizo «un prototipo de un prototipo» de lo que acabó siendo el core loop definitivo, y le
> costó «menos de dos días». Ese es el tamaño correcto de un prototipo.

---

## 7 · Playtesting

### 7.1 · La postura correcta

Valve lo formula como método científico: **los diseños son hipótesis, los playtests son
experimentos**; se evalúa el diseño contra el resultado y se repite. Y el objetivo declarado de
la sesión es **la diversión** — no cazar bugs, no balancear, y desde luego no un *focus group*.

La regla operativa que sale de ahí, y que cuesta más de cumplir de lo que parece:

> 🔺 **No ayudes. No expliques. No te justifiques.** Durante el desarrollo de *Half-Life*, los
> observadores de Valve **tenían prohibido decir nada** durante la sesión; solo podían arrancar
> y reiniciar tras un cierre inesperado. Hicieron más de **200 sesiones de dos horas**, con un
> tester externo y dos observadores detrás, y cada sesión producía en promedio **un centenar de
> puntos de acción**. Si tienes que explicar algo, el fallo es del juego, no del tester.

### 7.2 · Qué preguntar y qué no

| ✅ Pregunta | ❌ No preguntes | Por qué |
|---|---|---|
| «¿Qué estabas intentando hacer ahí?» | «¿Te ha gustado?» | La segunda solo mide educación |
| «¿Qué esperabas que pasara al pulsar eso?» | «¿Era demasiado difícil?» | Sugiere la respuesta |
| «Cuéntame qué pasó en ese momento» | «¿Te gustaría que hubiera un mapa?» | El jugador detecta problemas muy bien y propone soluciones muy mal |
| «¿Qué ibas a hacer a continuación?» | «¿Entendiste que el botón X hacía Y?» | Le estás enseñando la mecánica que querías medir |

El protocolo estándar es **pensar en voz alta** (*think-aloud*), «sin inducir ni corregir»: el
tester narra lo que hace y por qué; tú callas y escribes. Las preguntas van **al final**.

### 7.3 · Cuánta gente, cada cuánto

**Cinco personas por ronda, varias rondas.** Jakob Nielsen mostró que cinco usuarios sacan a la
luz alrededor del **85 %** de los problemas de usabilidad, y que con el mismo presupuesto es
mejor hacer **tres estudios de cinco** que uno de quince: los ciclos sirven para comprobar si el
arreglo funcionó. ⚠️ El dato procede de la usabilidad de interfaces, no de un estudio específico
de videojuegos; el orden de magnitud se sostiene, pero un problema de *diversión* aparece más
tarde que uno de usabilidad.

Regla de conteo al vaciar las notas: **1 de 5 es ruido · 3 de 5 es el diseño.**

### 7.4 · Cómo registrar

Una tabla de cuatro columnas por sesión, rellenada en vivo, más grabación de pantalla y audio:

| Minuto | Qué hizo (observable) | Qué dijo (literal) | Hipótesis (después, no durante) |
|---|---|---|---|
| 03:10 | Intenta saltar el hueco 4 veces | «esto no llega, ¿no?» | El hueco parece franqueable y no lo es |
| 07:45 | Ignora el cofre y sigue | — | El cofre no se lee como cofre |
| 12:02 | Deja el mando | «vale, ya lo pillo» | Aquí termina la curiosidad: falta un gancho |

**Separa observación de interpretación.** La columna 4 se rellena después de la sesión; si la
rellenas en vivo dejarás de mirar.

---

## 8 · El documento de diseño ligero

Un GDD de 60 páginas se escribe una vez y no lo lee nadie. Lo que funciona son **dos artefactos
cortos y vivos**: una página para el proyecto entero y una ficha por sistema. Ambos están
pensados para que **un LLM pueda rellenarlos y luego programar contra ellos** sin inventarse
nada.

### 8.1 · GDD de una página — plantilla

```markdown
# <Título> · GDD de una página          versión: 0.1 · fecha: AAAA-MM-DD

**Pitch (una frase, sin adjetivos):**
**Estéticas objetivo (MDA, dos, en orden):**   1.            2.
**Referencias y qué tomo de cada una:**
**Plataforma · duración de partida · público:**

**Verbos (máximo 5):**
**Bucle de acción (segundos):**    ____ para conseguir ____, que permite ____ mejor.
**Bucle de sesión (minutos):**
**Bucle de meta (horas):**         (o «no hay, es un arcade» — decidirlo, no olvidarlo)

**Victoria / derrota:**
**Forma de la curva de dificultad:**  rampa · dientes de sierra · escalones · pico y valle
**Qué hace este juego que no haga la referencia:**

**RECORTE — lo que NO va a estar:** (lista explícita; sin ella el proyecto no termina)
**Riesgo nº 1 y prototipo que lo responde:**
**Cómo sabré que funciona:** (la métrica o la observación concreta)
```

### 8.2 · Ficha por sistema — plantilla

```markdown
# Sistema: <nombre>                      estado: idea · prototipo · implementado · balanceado

**Para qué existe:** (una frase, en términos de la estética a la que sirve)
**Entradas:** qué lo alimenta y desde dónde
**Salidas:** qué produce y quién lo consume
**Estado que mantiene:** (variables; dónde viven: instancia / struct global / archivo)

**Reglas:** numeradas, en imperativo, comprobables
  R1.
  R2.

**Parámetros de balance:**
| Nombre | Valor inicial | Rango razonable | Dónde vive |
|---|---|---|---|
|  |  |  | `scr_config` · `balance.json` · room |

**Interacciones con otros sistemas:** (una línea por sistema tocado)
**Feedback al jugador:** qué ve, qué oye, en qué evento se dibuja
**Casos borde:** (qué pasa con 0, con el máximo, al pausar, al cambiar de sala)
**Cómo se prueba:** el gesto concreto que dice si funciona
**Telemetría:** qué evento registra y con qué campos
```

### 8.3 · Qué se fija antes de programar y qué se decide jugando

| Se fija **antes** (cambiarlo obliga a rehacer código) | Se decide **jugando** (cambiarlo es tocar un número) |
|---|---|
| Los verbos y el bucle de acción | El daño, la vida, el coste, la cadencia |
| Qué sistemas existen y quién habla con quién | El ritmo de aparición de enemigos |
| El formato de los datos (`balance.json`, tablas) | La forma exacta de la curva de dificultad |
| Dónde vive el estado (instancia, global, archivo) | El orden de las salas y qué enseña cada una |
| La condición de victoria y de derrota | Los textos, los nombres y los precios |

> 🔺 **Todo lo de la columna derecha debe poder cambiarse sin recompilar.** Si para probar otro
> daño hay que compilar 40 segundos, harás diez pruebas al día en vez de doscientas, y el juego
> quedará peor balanceado. Ese es todo el argumento de [§9](#9--cómo-se-traduce-a-gamemaker).

---

## 9 · Cómo se traduce a GameMaker

### 9.1 · Dónde vive cada decisión de diseño

| Tipo de decisión | Dónde vive | Por qué ahí |
|---|---|---|
| Constantes estructurales que no cambiarán (tamaño de tile, fps) | `#macro` en un script `scr_config` | Se sustituyen al compilar: coste cero y Feather avisa si escribes mal el nombre |
| Números que vas a tocar cientos de veces (daño, vida, coste, cadencia) | `balance.json` en **Included Files** → `global.balance` | Se cambian **sin recompilar** y se ajustan en caliente con el overlay |
| Tablas de contenido de 20 filas o más (enemigos, objetos, oleadas) | Hoja de cálculo → CSV/JSON → array de structs | La hoja es la herramienta correcta para comparar 200 números |
| Composición y ritmo de un nivel | La **room**, en el editor | El editor de rooms *es* la herramienta de diseño de niveles |
| Elecciones del jugador (dificultad, asistencias, volumen) | Guardado en el *save area* | Es del jugador, no del diseño → [04 · 25](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) |

### 9.2 · `scr_config` — las constantes

```gml
/// scr_config — constantes de diseño. NO se tocan en caliente: si cambian, se recompila.
#macro JUEGO_FPS             60
#macro TILE                  16
#macro BALANCE_ARCHIVO       "balance.json"
#macro BALANCE_VERSION       "1.4.0"
#macro TELEMETRIA_ARCHIVO    "telemetria.json"
#macro TELEMETRIA_ACTIVA     true      // ponlo a false en la build pública
```

### 9.3 · Datos de balance en Included Files

`balance.json` va en **Included Files** del proyecto. Un ejemplo mínimo pero realista:

```json
{
  "version": "1.4.0",
  "jugador":  { "vida": 100, "velocidad": 3.2, "invencible_frames": 45 },
  "armas": {
    "pistola":  { "dano": 15, "cadencia": 12, "cargador": 8 },
    "escopeta": { "dano": 9, "perdigones": 6, "cadencia": 45, "cargador": 4 }
  },
  "enemigos": {
    "baba":    { "vida": 30,  "dano": 8,  "velocidad": 0.8 },
    "arquero": { "vida": 45,  "dano": 12, "velocidad": 1.2 },
    "bruto":   { "vida": 180, "dano": 25, "velocidad": 0.6 }
  },
  "economia": { "coste_base": 25, "coste_razon": 1.18, "oro_por_baba": 4 }
}
```

```gml
/// scr_balance — cargar, guardar y restaurar la tabla de balance

/// @description Carga balance.json a global.balance. Devuelve true si salió bien.
function balance_cargar() {
    if (!file_exists(BALANCE_ARCHIVO)) {
        show_debug_message($"[balance] no encuentro {BALANCE_ARCHIVO}");
        return false;
    }

    var _buffer = buffer_load(BALANCE_ARCHIVO);
    var _texto  = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);

    try {
        global.balance = json_parse(_texto);
    } catch (_error) {
        show_debug_message($"[balance] JSON inválido: {_error.message}");
        return false;
    }

    if (!is_struct(global.balance) || !struct_exists(global.balance, "version")) {
        show_debug_message("[balance] estructura inesperada");
        return false;
    }
    if (global.balance.version != BALANCE_VERSION) {
        // Aviso, no error: durante el ajuste esto pasa constantemente.
        show_debug_message($"[balance] versión {global.balance.version}, esperaba {BALANCE_VERSION}");
    }
    return true;
}

/// @description Escribe los valores ajustados. Al escribir, el archivo se crea en el
///              save area; en el siguiente arranque, buffer_load leerá ESE y no el
///              de Included Files. Ese es el truco del ajuste en caliente.
function balance_guardar() {
    var _json   = json_stringify(global.balance, true);
    var _buffer = buffer_create(string_byte_length(_json) + 1, buffer_grow, 1);
    buffer_write(_buffer, buffer_string, _json);
    buffer_save(_buffer, BALANCE_ARCHIVO);
    buffer_delete(_buffer);
    show_debug_message($"[balance] guardado en {game_save_id}{BALANCE_ARCHIVO}");
}

/// @description Borra la copia ajustada y vuelve a la de Included Files.
function balance_restaurar() {
    if (file_exists(BALANCE_ARCHIVO)) file_delete(BALANCE_ARCHIVO);
    balance_cargar();
}
```

> 🔺 **El truco tiene un filo.** La regla de resolución del sandbox lee **primero el save area
> y solo después el bundle** (ver [01 · 14 — Persistencia](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md)).
> Es lo que hace posible ajustar sin recompilar, y también lo que hace que un `balance.json`
> viejo tapado en el save area te vuelva loco: el juego ignora el que acabas de exportar. Por eso
> `balance_restaurar()` no es opcional, y por eso el botón que la llama está en el panel de §9.4.

**Si tu hoja de cálculo solo exporta CSV**, conviértelo a JSON **en la exportación** (una macro
de la hoja, un script de una línea en el pipeline) y deja que GML lea siempre JSON. Parsear CSV
en GML es posible con `string_split` + `struct_set`, pero añade un formato más que mantener y
un sitio más donde equivocarse.

> ⚠️ Si aun así lo parseas en GML, recuerda que **`real("abc")` lanza un error, no devuelve 0**:
> el manual avisa de que cualquier carácter que no sea cifra, signo menos, punto decimal o parte
> exponencial provoca un fallo. Comprueba antes con `string_digits`, o limpia la cadena con ella.

### 9.4 · Balance en caliente con el Debug Overlay

Los controles `dbg_*` construyen una ventana dentro del juego con deslizadores enganchados a
tus variables **por referencia**: mueves el deslizador y el valor cambia en el mismo fotograma.
Es la diferencia entre diez pruebas al día y doscientas.

```gml
/// obj_panel_balance · Create
if (!debug_mode) { instance_destroy(); exit; }    // en la build pública, ni existe
show_debug_overlay(true);

dbg_view("Balance", true);

dbg_section("Jugador");
dbg_slider(ref_create(global.balance.jugador, "velocidad"), 0.5, 8, "Velocidad", 0.1);
dbg_slider_int(ref_create(global.balance.jugador, "vida"), 1, 400, "Vida", 5);

dbg_section("Arma: pistola");
dbg_slider_int(ref_create(global.balance.armas.pistola, "dano"), 1, 100, "Daño", 1);
dbg_slider_int(ref_create(global.balance.armas.pistola, "cadencia"), 1, 90, "Cadencia (frames)", 1);
dbg_text_separator("TTK calculado en vivo");
ttk_baba  = 0;
ttk_bruto = 0;
dbg_watch(ref_create(self, "ttk_baba"),  "TTK baba (s)");
dbg_watch(ref_create(self, "ttk_bruto"), "TTK bruto (s)");

dbg_section("Sesión");
global.invencible = false;
dbg_checkbox(ref_create(global, "invencible"), "Invencible");
accion_guardar   = function() { balance_guardar(); };
accion_restaurar = function() { balance_restaurar(); };
dbg_button("Guardar balance", accion_guardar);
dbg_same_line();
dbg_button("Restaurar por defecto", accion_restaurar);

/// obj_panel_balance · Step
var _arma = global.balance.armas.pistola;
ttk_baba  = tiempo_para_matar(global.balance.enemigos.baba.vida,  _arma.dano, _arma.cadencia);
ttk_bruto = tiempo_para_matar(global.balance.enemigos.bruto.vida, _arma.dano, _arma.cadencia);
```

```gml
/// scr_formulas — las fórmulas de §4.4, en código

/// @description Segundos hasta matar. El primer golpe ocurre en el instante 0.
function tiempo_para_matar(_vida, _dano, _cadencia_frames) {
    if (_dano <= 0) return infinity;
    var _golpes = ceil(_vida / _dano);
    return (_golpes - 1) * (_cadencia_frames / JUEGO_FPS);
}

/// @description Coste geométrico de la mejora número _nivel (0 es la primera).
function curva_coste(_nivel) {
    var _e = global.balance.economia;
    return round(_e.coste_base * power(_e.coste_razon, _nivel));
}
```

**Lo que hay que saber antes de usar el panel** (detalle en
[01 · 15 — Depuración](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)):

- **La referencia va primero** en `dbg_slider`, `dbg_slider_int`, `dbg_watch` y `dbg_checkbox`;
  la etiqueta, después. `dbg_button` es la excepción: **etiqueta primero, función después**.
- **No se puede referenciar una variable local** (`var _x`): tiene que vivir en una instancia,
  en un struct o en `global`. `ref_create` acepta `self`, `other`, `global` y un struct directo.
- El overlay **no funciona en HTML5**, y con el ratón encima **el juego no recibe eventos de
  teclado ni ratón**: `is_keyboard_used_debug_overlay()` te permite distinguirlo.
- `dbg_view()` y `dbg_section()` se llaman **una sola vez**, en un Create — nunca en el Step.

### 9.5 · Telemetría: contar muertes por sala y volcarlas a JSON

```gml
/// scr_telemetria — el registro mínimo que paga su coste desde el primer playtest

function telemetria_iniciar() {
    global.telemetria = {
        sesion  : $"{date_datetime_string(date_current_datetime())}#{irandom(9999)}",
        balance : BALANCE_VERSION,
        inicio  : get_timer(),
        eventos : []
    };
}

/// @description Anota un evento con su sala y su marca de tiempo.
/// @param {String} _tipo    "muerte", "sala_entra", "sala_sale", "compra"…
/// @param {Struct} _extra   Campos propios del evento. Opcional.
function telemetria_registrar(_tipo, _extra = undefined) {
    if (!TELEMETRIA_ACTIVA) return;

    var _evento = {
        tipo : _tipo,
        sala : room_get_name(room),
        ms   : (get_timer() - global.telemetria.inicio) div 1000   // microsegundos → ms
    };

    if (is_struct(_extra)) {
        var _campos = struct_get_names(_extra);
        for (var _i = 0; _i < array_length(_campos); _i++) {
            struct_set(_evento, _campos[_i], struct_get(_extra, _campos[_i]));
        }
    }

    array_push(global.telemetria.eventos, _evento);
}

/// @description Vuelca todo lo registrado a un JSON del save area.
function telemetria_volcar() {
    if (!TELEMETRIA_ACTIVA) return;
    if (array_length(global.telemetria.eventos) == 0) return;

    var _json = json_stringify(global.telemetria, true);
    var _f = file_text_open_write(TELEMETRIA_ARCHIVO);
    file_text_write_string(_f, _json);
    file_text_close(_f);

    show_debug_message($"[telemetría] {array_length(global.telemetria.eventos)} eventos"
                     + $" → {game_save_id}{TELEMETRIA_ARCHIVO}");
}
```

Dónde se llama a cada cosa:

| Evento del objeto | Llamada |
|---|---|
| `obj_arranque` · Create | `telemetria_iniciar();` |
| Cualquier objeto · **Room Start** | `telemetria_registrar("sala_entra");` |
| Cualquier objeto · **Room End** | `telemetria_registrar("sala_sale"); telemetria_volcar();` |
| `obj_jugador` · Destroy (o donde muera) | `telemetria_registrar("muerte", { causa: causa_muerte, intento: global.intentos, x_muerte: x, y_muerte: y });` |
| `obj_arranque` · **Game End** | `telemetria_volcar();` |

> 🔺 **Vuelca en cada Room End, no solo al salir.** El evento *Game End* no está garantizado en
> todas las plataformas (un cierre forzado en móvil se lo salta), y un playtest cuyos datos se
> pierden es un playtest perdido. Reescribir el archivo entero cada sala es de sobra rápido para
> unos miles de eventos.
>
> ⚠️ **`analytics_event()` existe en el runtime pero está marcada como obsoleta**: no la uses.
> Y **no envíes telemetría a ningún servidor sin decírselo al jugador**: en la build de playtest
> con amigos, el JSON local basta y no tiene implicaciones legales.

### 9.6 · Leer el volcado

Para la pregunta de siempre —*¿qué sala mata más?*— basta una línea con
[`jq`](https://jqlang.github.io/jq/):

```sh
jq '[.eventos[] | select(.tipo=="muerte") | .sala]
    | group_by(.) | map({sala: .[0], muertes: length})
    | sort_by(-.muertes)' telemetria.json
```

```json
[ { "sala": "rm_zona1_07", "muertes": 34 }, { "sala": "rm_zona1_04", "muertes": 9 } ]
```

Con cinco testers, `rm_zona1_07` acumulando 34 de 46 muertes no es una opinión: es un muro.
Vuelves a §3.2 y decides si ese pico va donde está o si le falta el diente anterior.

---

## 10 · Checklist

**Antes de escribir una línea de GML**

- [ ] Los **verbos** están escritos y son cinco o menos; las **dos estéticas objetivo** (MDA), elegidas y ordenadas
- [ ] La frase del bucle está rellena: *«el jugador ___ para conseguir ___, que le permite ___ mejor»*
- [ ] Los tres bucles están dibujados, o se ha decidido **a propósito** que falta alguno
- [ ] La casilla **[5] CAMBIO** no está vacía y la **[4] DECISIÓN** tiene más de una opción buena
- [ ] El **recorte** está escrito, y el riesgo nº 1 tiene prototipo con pregunta y presupuesto

**Antes de balancear**

- [ ] Cada recurso tiene **fuente y sumidero**, y la realimentación positiva tiene freno
- [ ] Los números vivos están en `balance.json`, no repartidos por el código
- [ ] Existe un **golpe estándar**, y el TTK de cada enemigo está calculado, no adivinado

**Antes de enseñárselo a alguien**

- [ ] `obj_panel_balance` ajusta sin recompilar, y `balance_restaurar()` tiene botón
- [ ] La telemetría registra `sala_entra`, `sala_sale` y `muerte`, y **vuelca en Room End**
- [ ] La primera pantalla contesta *quién soy · qué puedo hacer · adónde voy · qué me mata* sin texto
- [ ] Cada mecánica tiene sus cuatro encuentros: presentar, ampliar, combinar, examinar

**En el playtest**

- [ ] Cinco personas por ronda, varias rondas, y tú **no hablas ni explicas**
- [ ] La columna «hipótesis» de la plantilla se rellena **después** de la sesión
- [ ] `TELEMETRIA_ACTIVA` a `true` en la build de prueba… y a `false` en la que publicas

---

## 11 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo se evita |
|---|---|---|
| **Confundir características con diseño** | Una lista de cosas guays parece un plan | Rellena la frase del bucle antes que la lista |
| **Añadir un sistema para arreglar otro** | El sistema roto es más difícil de arreglar que de tapar | Un sistema nuevo solo entra si **modifica** a uno existente |
| **Ajustar el balance recompilando** | No se conocen los controles `dbg_*` | El panel de §9.4 cuesta 20 minutos y devuelve semanas |
| **Un `balance.json` fantasma en el *save area*** | La regla de resolución lee primero el *save area* | `balance_restaurar()`, y saberlo |
| **Enseñar dos mecánicas en la misma pantalla** | El nivel iba corto de contenido | Una idea nueva cada vez; si sobra sitio, repite la anterior con variación |
| **Preguntar «¿te ha gustado?»** | Es la pregunta natural | «¿Qué estabas intentando hacer ahí?» |
| **Ayudar al tester** | Cuesta mucho callarse | Si tienes que explicarlo, el fallo es del juego |
| **Fiarse de la media en la telemetría** | Es lo que sale por defecto | Mediana, siempre |
| **Refactorizar el prototipo en vez de tirarlo** | Da pena borrar código que funciona | El prototipo entrega **una respuesta**, no código |
| **DDA oculta sobre la vida del jefe** | Parece elegante | El jugador la nota y su victoria deja de ser suya; usa asistencia explícita |

---

## Ver también

- [02 — Diseño de niveles](./02%20-%20Diseño%20de%20niveles.md) — el oficio de convertir estas decisiones en salas concretas; §5 de aquí es su puerta de entrada
- [11 — Producción, alcance y lanzamiento](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) — qué pasa con el GDD y el recorte cuando hay calendario
- [04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) — el plano del juego entero; este documento decide **qué** se monta ahí
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) — el feedback del paso 3 del bucle de aprendizaje
- [04 · Índice de recetas](../04%20-%20Recetas%20por%20género/_INDICE-RECETAS.md) — la ruta de aprendizaje por géneros y el criterio para avanzar de fase
- [04 · 11 — Arcade y juegos de un botón](../04%20-%20Recetas%20por%20género/11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) — una curva de dificultad **ya implementada** (`DifficultyCurve`)
- [04 · 05 — Roguelike](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) (dificultad por piso, loot ponderado) y [04 · 08 — Tower Defense](../04%20-%20Recetas%20por%20género/08%20-%20Tower%20Defense.md) (economía de oleadas: el caso más claro de fuentes y sumideros)
- [04 · 25 — Menú de opciones y ajustes](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) · [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — dónde vive la asistencia explícita
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) — el Debug Overlay y las vistas `dbg_*` explicadas de cero
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el *sandbox*, la regla de resolución y `json_stringify` / `json_parse`
- [01 · 04 — Structs y constructores](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) — la forma correcta de guardar tablas de balance
- [05 · 04 — Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — nombres, prefijos y variables reservadas
- [06 · `scr_debug.gml`](../06%20-%20Assets%20y%20Scripts/scr_debug.gml) — panel propio, alternativa al overlay cuando necesitas HTML5 · [12 · 05 — Pipeline](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) — el resto del pipeline de datos externos
- [RUTA.md](../RUTA.md) — este documento es material de nivel 3 en adelante

---

## Fuentes

Todas consultadas el **2026-09-06**.

**Marco teórico**

- Robin Hunicke, Marc LeBlanc y Robert Zubek — *MDA: A Formal Approach to Game Design and Game
  Research* (2004) — <https://users.cs.northwestern.edu/~hunicke/MDA.pdf> · definiciones de
  Mechanics/Dynamics/Aesthetics, las perspectivas opuestas de diseñador y jugador, las 8 «kinds of
  fun» y los ejemplos de realimentación (termostato, Monopoly)
- Tynan Sylvester — *Designing Games: A Guide to Engineering Experiences*, O'Reilly, 2013 ·
  definición de **elegancia** y de **emergencia**, y los tres «olores» de la elegancia
- Ernest Adams y Joris Dormans — *Game Mechanics: Advanced Game Design*, New Riders, 2012 —
  muestra oficial del editor:
  <https://ptgmedia.pearsoncmg.com/images/9780321820273/samplepages/0321820274.pdf> · definiciones
  de *sources*, *drains*, *converters* y *traders*; es el libro que originó **Machinations**
  (<https://machinations.io/>)
- Jenova Chen — *Flow in Games*, tesis de máster, USC, 2006 —
  <https://www.jenovachen.com/flowingames/Flow_in_games_final.pdf> · la banda de flow entre
  aburrimiento y ansiedad, y la advertencia sobre lo poco trivial que es publicar una DDA
- Jesse Schell — *The Art of Game Design: A Book of Lenses* —
  <https://schellgames.com/art-of-game-design> · la lente de la Experiencia Esencial, la del
  Tétrada Elemental y la del Flow. ⚠️ Verificado sobre el texto de la 1.ª edición (Morgan
  Kaufmann, 2008); **no** se pudo abrir el de la 3.ª edición (Routledge/CRC, 2019): la numeración
  de las lentes y el recuento exacto de esa edición quedan sin verificar
- Daniel Cook — *Loops and Arcs*, Lostgarden, 30 de abril de 2012 —
  <https://lostgarden.com/2012/04/30/loops-and-arcs/> · el bucle modelo mental → acción →
  simulación → feedback, y la distinción bucle/arco

**Playtesting y dificultad**

- Mike Ambinder (Valve) — *Valve's Approach to Playtesting: The Application of Empiricism*, GDC
  2009 —
  <https://cdn.akamai.steamstatic.com/apps/valve/2009/GDC2009_ValvesApproachToPlaytesting.pdf> ·
  «los diseños son hipótesis, los playtests son experimentos»; el protocolo *think-aloud* «sin
  inducir ni corregir»; medir lo que la gente hace, no lo que dice
- Ken Birdwell — *The Cabal: Valve's Design Process for Creating Half-Life*, Game Developer,
  diciembre de 1999 —
  <https://www.gamedeveloper.com/design/the-cabal-valve-s-design-process-for-creating-i-half-life-i->
  · más de 200 sesiones de dos horas, un tester y dos observadores, observadores en silencio, ~100
  puntos de acción por sesión
- Jakob Nielsen — *Why You Only Need to Test with 5 Users*, Nielsen Norman Group, 18 de marzo de
  2000 — <https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/> · cinco
  usuarios descubren ~85 % de los problemas; mejor tres estudios de cinco que uno de quince. ⚠️ Es
  investigación de usabilidad de interfaces, no de diversión en videojuegos
- Patrick Klepek — *Why The Very Hard «Celeste» is Perfectly Fine With You Breaking Its Rules*,
  Vice, 7 de febrero de 2018 — <https://www.vice.com/en/article/celeste-difficulty-assist-mode/> ·
  declaraciones directas de Maddy Thorson sobre el modo asistido y sobre por qué dejó de llamarse
  «Cheat Mode»
- Kim Swift y el equipo de Valve — *A Portal Post-Mortem: Integrating Writing and Design*, GDC
  2008 — ficha en <https://archive.org/details/GDC2008Swift>. ⚠️ Solo se pudo verificar la ficha
  de la sesión: el contenido está tras el muro de pago de GDC Vault, así que **nada de este
  documento se apoya en ella**

**GameMaker**

- Manual oficial LTS — *The Debug Overlay* —
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/The_Debug_Overlay.htm>
  (espejo local en `09 - Manual oficial/manual-lts-2026-es/…/Debugging/`)
- Manual oficial LTS — `ref_create` —
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/ref_create.htm>
  · acepta `self`, `other`, `global` y structs; no admite variables locales
- Manual oficial LTS — `real` —
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/real.htm>
  · los caracteres no numéricos provocan un error
- Manual oficial LTS — `json_stringify` / `json_parse` —
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing.htm>
- Andrew Turner — *The Long Journey Of DYO*, blog oficial de GameMaker, 21 de febrero de 2018 —
  <https://gamemaker.io/en/blog/the-long-journey-of-dyo> · prototipado analógico con bloques de
  madera antes de programar
- Samuel Wain — *From GameMaker to Unity and Back: Finding the Right Brush*, blog oficial de
  GameMaker, 9 de mayo de 2025 —
  <https://gamemaker.io/en/blog/bancyco-gamemaker-to-unity-and-back> · el «prototipo de un
  prototipo» del core loop, en menos de dos días

**Marcado con ⚠️ en el texto.** La lectura del nivel 1-1 de *Super Mario Bros.* (§5.1) es
consenso crítico, no una declaración publicada por Nintendo. Las heurísticas de TTK (§4.4) son
reglas de oficio, sin fuente primaria que las fije en cifras. El 85 % de Nielsen (§7.3) procede
de usabilidad de interfaces y aquí se extrapola. De Schell no se pudo abrir la 3.ª edición, y de
la charla de *Portal* solo la ficha: **nada del documento se apoya en ellas**.
