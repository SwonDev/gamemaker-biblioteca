# 14 · El documento de diseño — del one-pager al GDD completo

> **Cuándo el GDD de una página deja de bastar, y qué se escribe en su lugar.**
> [13 · 01 §8](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#8--el-documento-de-diseño-ligero)
> ya da los dos artefactos que sirven en el 90 % de los proyectos —el GDD de una página y la
> ficha por sistema— y este documento **no los repite**. Empieza justo donde ese `§8` lo deja:
> los cuatro casos en los que una página no alcanza, la plantilla completa por secciones (con
> qué va, qué NO va y en qué documento de esta biblioteca está ya resuelto cada bloque), los
> pilares de diseño, el elevator pitch, la wiki viva frente al documento congelado, y un
> catálogo de los diagramas de diseño que no tienen dueño en ningún otro documento.
>
> **Qué NO cubre.** Cómo se diseña cada sistema por dentro (economía, dificultad, progresión)
> está en [13 · 01](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md).
> Cómo se planifica el calendario, se estima el alcance y se llega a lanzamiento está en
> [13 · 11](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md), que este documento enlaza en
> vez de repetir. El canon teórico más allá de MDA y Flow (Koster, Salen & Zimmerman, Schell,
> Bartle) y el diseño de negocio y monetización quedan fuera de esta biblioteca a fecha de hoy:
> son huecos señalados en la auditoría de `_indice/auditorias/diseno-gdd.md` y no se rellenan
> aquí para no fingir una cobertura que no existe.

---

## 1 · Los principios

### 1.1 · Cuándo el one-pager no basta

El GDD de una página de `13/01 §8.1` es la opción por defecto. Escribir uno completo, con
secciones para cada sistema, es **más caro de mantener** que de redactar: cada sección que
añades es una superficie más que puede quedarse desactualizada. La pregunta correcta no es «¿mi
juego se merece un GDD grande?», es «¿qué me va a costar **no** tenerlo». Cuatro señales, y con
una sola ya compensa:

1. **Sois más de una persona escribiendo código o arte a la vez.** Una página no reparte trabajo
   sin ambigüedad: dos personas necesitan saber, sin preguntarse, quién es dueño de qué sistema y
   qué asume cada uno del otro.
2. **Hay un editor (*publisher*), financiación pública o un inversor.** Van a pedir un documento
   que puedan leer sin conocer el proyecto de memoria: mercado, plataformas, calendario, riesgo.
   El pitch de una línea no sustituye esa conversación, la resume.
3. **El proyecto va a vivir más de un ciclo de dos semanas del §3.4 de `13/11`** — es decir, más
   de unos pocos meses, o va a pasar por manos que hoy no están en el proyecto (colaboradores que
   se suman tarde, o tú mismo dentro de un año sin memoria fresca).
4. **Un LLM va a implementar veinte sistemas a partir de este documento.** Es el caso de uso
   propio de esta biblioteca ([§6](#6--la-versión-para-llm-qué-necesita-un-agente-para-implementar-sin-inventar)
   lo desarrolla entero): un agente no tiene el contexto tácito que tiene un compañero humano, así
   que la ambigüedad que un humano rellenaría preguntando, el agente la rellena **inventando**. Un
   documento completo, con reglas numeradas y parámetros con rango, es lo que evita eso — y esa
   ambigüedad no es solo de mecánicas: un GDD que nunca menciona el envoltorio del juego
   (splash, menú, pausa, opciones, créditos) deja que el agente decida por su cuenta si eso
   cuenta como parte del encargo. La fila **2.14 bis** de [§2](#2--el-método-paso-a-paso) y el
   checklist maestro de
   [04 · 00](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#el-checklist-de-juego-completo)
   existen para que esa ambigüedad concreta no dependa de que quien redacta el GDD se acuerde.

Si ninguna de las cuatro aplica, vuelve a `13/01 §8` y no sigas leyendo: escribir un GDD de 40
páginas para un juego de una persona y seis semanas es el propio **feature creep** de `13/11 §1.6`
aplicado a la documentación.

### 1.2 · Qué es (y qué no es) un GDD completo

La referencia histórica del oficio es Tim Ryan, *The Anatomy of a Design Document* (Gamasutra,
19-10-1999): un documento de diseño «expresa la visión con detalle suficiente para
implementarla», y cumple un papel distinto según quién lo lee — es la **biblia** desde la que el
productor predica el objetivo, la vía por la que el diseñador defiende sus ideas, y de la que
programadores y artistas sacan instrucciones. Esa cita de 1999 sigue siendo el resumen más
honesto de para qué sirve, y explica por qué un GDD malo no falla por estar mal escrito: falla
por intentar ser las tres cosas a la vez sin decidir para cuál se optimiza.

Lo que este documento **NO** propone es la estructura literal de Ryan (concepto → propuesta →
especificación funcional en tres documentos separados, pensada para un estudio de 1999 con
productor, diseñador y programador como roles distintos). La plantilla de [§2](#2--el-método-paso-a-paso)
está reordenada para un desarrollo pequeño o solitario, y con foco en lo que **este** proyecto —una
biblioteca para que un LLM desarrolle con GameMaker sin inventarse nada— necesita de verdad: que
cada sección diga de dónde saca sus números y qué documento de esta biblioteca ya lo resuelve.

Un GDD completo tampoco es una promesa de que el juego se hará así. Es, como dice la cita de
Ryan, **detalle suficiente para implementar** — no detalle definitivo. La tabla de `13/01 §8.3`
(qué se fija antes de programar y qué se decide jugando) se aplica exactamente igual aquí, sección
por sección: algunas partes de este documento son contrato, otras son la mejor hipótesis del día
en que se escribió.

### 1.3 · Pilares de diseño: 3-5 frases que resuelven discusiones

Un pilar de diseño no es una característica ni un elemento de la trama: es una frase afirmativa
sobre la **experiencia** que el juego quiere producir, y su prueba de fuego es que sirve para
**resolver una discusión sin necesidad de que decida la persona con más rango**. Max Pears lo
resume en *Design Pillars: The Core of Your Game* (Game Developer, 12-10-2017): 3 a 5 pilares,
y ante cualquier mecánica nueva la pregunta es «¿esto sirve a alguno de nuestros pilares?» — si la
respuesta es no, la mecánica sale, por bonita que sea. El artículo cita *The Last of Us*
(Crafting, Story, AI Partners, Stealth) y *Breath of the Wild* (Exploration, Traversal,
Scavenging, Options, Combat) como ejemplo de que un pilar a veces es una mecánica y a veces un
concepto — lo que importa es que **oriente**, no que tenga una forma fija.

**Cómo se derivan.** No se inventan en una reunión de una hora sobre una pizarra en blanco: salen
de las **estéticas objetivo (MDA)** que ya elegiste en `13/01 §1.3` y de la frase del bucle de
`13/01 §2.2`. Si tu bucle es «esquivar → gemas → elegir mejora», un pilar candidato es «el riesgo
siempre es visible antes de tomarlo» — porque es la condición que hace que esquivar sea una
decisión y no un reflejo.

**Ejemplo de discusión resuelta.** Un plataformas con los pilares:

```
P1. El salto es el único verbo de combate: no hay ataque, solo esquiva y sincronización.
P2. Cada muerte es instantánea y el respawn es inmediato (< 0,5 s): no hay pantalla de carga.
P3. La luz es un recurso visible que se agota: nunca hay temporizador invisible.
```

Alguien del equipo propone un enemigo que dispara un proyectil que hay que golpear de vuelta.
Contra P1, la respuesta es automática y no depende de gustos: **no**, porque introduce un verbo de
combate nuevo. La misma propuesta, reformulada como «un proyectil que hay que esquivar
agachándose», sí pasa el filtro. Eso es lo que compra un pilar bien escrito: la discusión dura
diez segundos en vez de una reunión.

**Qué NO es un pilar.** «Gráficos bonitos», «que sea divertido» o «buena jugabilidad» no sirven
para decidir nada porque cualquier propuesta los cumple. Si un pilar no puede **rechazar** al
menos una idea razonable, no es un pilar: es una aspiración.

### 1.4 · El elevator pitch: fórmula, qué NO lleva, venta frente a diseño

El pitch de una frase de `13/01 §8.1` ya pide «sin adjetivos». Aquí va el **cómo** se construye
uno que funcione fuera del documento, para alguien que no conoce el proyecto.

**La fórmula «X se encuentra con Y».** Es la forma más citada del oficio (Gamestorming, *Elevator
Pitch*): comparar el juego con dos referencias conocidas para dar una impresión rápida de algo
complejo. El ejemplo canónico de la industria es el pitch interno de *Viva Piñata: Party Animals*
— «*Mario Kart* se encuentra con *Mario Party*, en un episodio de *The Amazing Race*» — y uno más
reciente e indie: «*Blade Runner* al estilo de *Lovecraft Country*, ambientado en el *Sin City* de
Frank Miller». La fórmula no es infalible (dos juegos malos no hacen uno bueno por sumarse), pero
obliga a elegir **qué prestas de cada referencia**, que es la parte útil del ejercicio.

**Qué SÍ lleva, según la práctica del oficio** (Alex Nichiporchik, *How To Pitch Your Game*, Game
Developer, 17-09-2015): referencias que la otra persona ya conoce, una conexión emocional o un
gancho concreto («¿alguna vez quisiste apuñalar a tus vecinos ruidosos?»), y una frase que
sobrevive **dicha en voz alta**, no solo leída.

**Qué NO lleva:** explicaciones de mecánicas, trasfondo narrativo, ni una frase que necesite una
segunda frase para entenderse. Si tu pitch necesita una nota a pie de página, no es un pitch: es
un resumen.

**Pitch de venta frente a pitch de diseño.** No son el mismo texto, aunque el brief los confunda:

| | Pitch de venta | Pitch de diseño |
|---|---|---|
| Para quién | Prensa, tienda, un editor, un jugador que nunca ha visto el juego | El propio equipo, incluido tú dentro de seis meses |
| Prioriza | El gancho: qué hace que alguien quiera saber más en tres segundos | La estética objetivo (MDA) y qué se toma prestado de la referencia y qué NO |
| Dónde vive | La página de tienda (`13/11 §6.1`), el press kit (`13/11 §8.4`) | La casilla «Pitch» y «Qué hace este juego que no haga la referencia» de `13/01 §8.1` |
| Se puede mentir un poco | Sí, es marketing: exagera lo que engancha | No: si el pitch de diseño miente, el equipo construye el juego equivocado |

Fullerton (*Game Design Workshop*, cap. de *pitching*) trata esta distinción como la razón por la
que un pitch que convence a un editor a veces no sirve de brújula al equipo: resuelven problemas
distintos y confundirlos hace que el documento de diseño se lea como un anuncio.

### 1.5 · Wiki viva frente a documento congelado

Un GDD que se escribe una vez y no se vuelve a tocar **miente desde el segundo cambio de
diseño** que no se refleja en él. La alternativa no es «no documentar»: es tratar el documento
como un artefacto vivo, con las mismas reglas de un repositorio de código.

**La cita que resume por qué.** Rodolfo Rubens, desarrollador indie, en *How to Write a Game
Design Document* (Nuclino, actualizado 12-01-2026): «los documentos de diseño de juego están muy
vivos. Siempre estamos prototipando y cambiando de idea sobre cómo va a funcionar algo». El mismo
artículo señala el riesgo simétrico: tratar el GDD como un plano rígido «mata la creatividad del
equipo» tanto como no documentar nada.

**Dónde vive.** No hace falta herramienta especial: `13/11 §3.7` ya compara archivos `.md` en el
repo, GitHub Projects, Trello, Notion y HacknPlan, con el mismo criterio que aplica aquí — usa
**una sola**, y que esté donde ya trabajas. Esta biblioteca es, ella misma, un wiki vivo
versionado con Git (`_indice/actualizar.py` la mantiene sincronizada); si tu proyecto sigue el
mismo patrón — Markdown en el repo, junto al código — el documento de diseño se revisa en el mismo
*pull request* que el código que lo implementa, y el historial de Git **es** el historial de
decisiones de diseño.

**Quién gana cuando el código y el documento discrepan.** Gana el código que está en producción,
siempre — pero la discrepancia no se queda muda: se escribe un ADR ligero
(`13/11 §3.5`, un archivo de cinco líneas en `decisiones/`) que dice qué cambió, por qué, y
actualiza el documento en el mismo commit. Sin ese paso, la próxima persona que lea el documento
completo va a **confiar en un texto que ya no es verdad**, que es peor que no tener documento.
El diario de desarrollo de `13/11 §3.6` cumple el mismo papel a escala diaria: tres líneas al
terminar cada sesión evitan que la memoria de por qué se decidió algo viva solo en la cabeza de
quien lo decidió.

**La regla de caducidad.** Una sección de este documento que nadie ha tocado en el ADR ni en el
diario en las últimas dos semanas de desarrollo activo **no es que esté terminada: puede que esté
abandonada**. No hace falta un proceso para esto — basta con que la revisión de cada ciclo de dos
semanas de `13/11 §3.4` incluya un vistazo a qué sección del GDD tocó el trabajo de esas dos
semanas, y si el documento sigue diciendo lo mismo que decía antes.

---

## 2 · El método, paso a paso

La tabla siguiente es la plantilla completa por secciones. Cada fila dice **qué va**, **qué NO
va** (y a qué otro apartado de esta misma tabla o de la biblioteca pertenece eso que no va) y
**dónde está ya desarrollado** el contenido de esa sección — con el enlace exacto. La regla que
gobierna toda la tabla es la de `AGENTS.md`: si algo ya está resuelto en otro documento, aquí se
enlaza y no se repite.

| # | Sección | Qué va aquí | Qué NO va aquí | Dónde está desarrollado |
|---|---|---|---|---|
| 2.1 | **Portada y control de versión** | Título, una línea de estado (idea / prototipo / vertical slice / producción), versión y fecha, quién lo mantiene | El pitch (va en 2.2) | Formato en [§3.4](#34--la-plantilla-completa-lista-para-copiar) de este documento |
| 2.2 | **Concepto y pitch** | El pitch de venta y el de diseño ([§1.4](#14--el-elevator-pitch-fórmula-qué-no-lleva-venta-frente-a-diseño)), las referencias y qué se toma de cada una, «qué hace este juego que no haga la referencia» | Los pilares (van en 2.3), el público (va en 2.4) | Casilla «Pitch» y «Referencias» de [13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla) |
| 2.3 | **Pilares de diseño** | 3-5 frases afirmativas y el criterio para usarlas en una discusión | Las estéticas MDA en sí (son la entrada, no la salida) | [§1.3](#13--pilares-de-diseño-3-5-frases-que-resuelven-discusiones) de este documento; MDA en [13 · 01 §1.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#13--mda-mecánica--dinámica--estética) |
| 2.4 | **Público, plataformas y competencia** | A quién sirve el juego sin inventárselo, qué cambia por plataforma, 3-5 juegos de referencia con su fortaleza y su debilidad frente al tuyo | Un estudio de mercado completo (fuera de alcance para un equipo pequeño) | [§2.5](#25--público-plataformas-y-competencia-el-método) de este documento (nuevo) |
| 2.5 | **Core loop y bucles anidados** | Los tres relojes (acción/sesión/meta), la frase del bucle, el diagrama de cinco casillas | La curva de dificultad (va en 2.8) | [13 · 01 §2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#2--el-core-loop-y-los-bucles-anidados) |
| 2.6 | **Mecánicas y verbos** | Los verbos (máximo 5), mecánicas frente a sistemas, la regla del segundo sistema | La ficha detallada de cada sistema (va en 2.7) | [13 · 01 §1.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#15--mecánicas-frente-a-sistemas) |
| 2.7 | **Sistemas** | Una ficha por sistema (entradas, salidas, estado, reglas numeradas, parámetros de balance, casos borde, telemetría) | Los números finales de balance (viven en `balance.json`, no en el documento — 2.9) | [13 · 01 §8.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#82--ficha-por-sistema--plantilla) |
| 2.8 | **Progresión y dificultad** | Forma de la curva, XP y niveles si aplica, DDA sí/no y por qué | Árboles de habilidades y meta-progresión con método propio (va en el propio [13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md), que ya cierra este hueco) | [13 · 01 §3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#3--progresión-y-curva-de-dificultad) y [13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md) para el árbol de habilidades y la meta-progresión entre partidas |
| 2.9 | **Economía y balance** | Fuentes, sumideros, convertidores; la regla de inflación; fórmulas con TTK y los números reales | La simulación Monte Carlo y la caza de dominancia (van en el propio [13 · 21](./21%20-%20Balance%20por%20simulación%20-%20Monte%20Carlo%2C%20Machinations%20y%20estrategias%20dominantes.md), que ya cierra este hueco) | [13 · 01 §4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#4--economía-y-balance) y [13 · 21](./21%20-%20Balance%20por%20simulación%20-%20Monte%20Carlo%2C%20Machinations%20y%20estrategias%20dominantes.md) para la notación formal de Machinations y la simulación |
| 2.10 | **Niveles y mundo** | Tipo de estructura (lineal, hub, metroidvania…), la hoja de nivel por cada nivel | El pixel art de los tiles (va en 2.12) | [13 · 02](./02%20-%20Diseño%20de%20niveles.md), hoja de nivel en [§4](./02%20-%20Diseño%20de%20niveles.md#4--la-hoja-de-nivel-la-plantilla-que-se-rellena-antes-de-construir) |
| 2.11 | **Personajes, mundo y narrativa** | Biblia del mundo de una página, ficha de personaje, mapa de ramas si hay elección | Diálogo línea por línea (vive en el guion, no en el GDD) | [13 · 12 §8](./12%20-%20Diseño%20narrativo%20y%20diálogos.md#8--plantillas) |
| 2.12 | **Arte y dirección visual** | Paleta, resolución base, referencias visuales, hoja de estilo de animación | El pipeline técnico Aseprite → GameMaker (va en 2.15) | [13 · 03](./03%20-%20Pixel%20art%20y%20resolución.md) y [13 · 04](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md) |
| 2.13 | **Audio** | Categorías de sonido, presupuesto, referencias de mezcla, hoja de sonido | La configuración de buses en código (va en 2.15) | [13 · 09](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) |
| 2.14 | **UI y UX** | Mapa de pantallas, taxonomía diegética, componentes necesarios | El nine-slice y el layout en píxeles (va en 2.15) | [13 · 05](./05%20-%20UI%20y%20UX%20de%20juego.md), mapa de pantallas en [§2.1](./05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada) |
| 2.14 bis | **Envoltorio de pantallas** | Marca cada pieza del envoltorio como presente o «no aplica: `<razón>`» — splash, menú principal, selección de nivel (si hay), pausa, opciones, créditos. No describe CÓMO se construye cada una (eso ya está en la columna de la derecha): solo obliga a que el GDD las nombre, para que no desaparezcan por omisión | El diseño detallado de cada pantalla (vive en 2.14, arriba) | [04 · 00 — el checklist maestro de «juego completo»](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#el-checklist-de-juego-completo); selección de nivel en [04 · 57](../04%20-%20Recetas%20por%20género/57%20-%20Selección%20de%20nivel%20y%20capítulo.md) |
| 2.15 | **Técnica y arquitectura** | Capas del proyecto, dónde vive el estado, formato de los datos, qué motor de físicas | El código en sí (vive en `.gml`, no en el GDD) | [13 · 06](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) |
| 2.16 | **Monetización y modelo de negocio** | Qué modelo (premium, F2P, DLC) y su efecto en el resto del diseño | La integración con Steamworks/AdMob/IAP (implementación, no diseño) | [13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md) para el criterio de diseño; implementación en [04 · 20](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md); precio y regiones en [13 · 11 §6.7](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#67-fecha-precio-y-regiones) |
| 2.17 | **Marketing y lanzamiento** | Cuándo publicar la página de tienda, activos necesarios, press kit, wishlists | El texto final del press kit (se rellena con la plantilla, no se redacta aquí) | [13 · 11 §6](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#6--lanzamiento) y [§8.4](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#84-press-kit) |
| 2.18 | **Calendario, alcance y equipo** | Fases con criterio de salida, la matriz de recorte, quién hace qué | La estimación día a día (vive en el tablero de `13/11 §3.1`, no en el GDD) | [13 · 11 §1-§3](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#1--alcance-el-único-problema-que-de-verdad-mata-juegos) |
| 2.19 | **Anexos: glosario y registro de cambios** | Términos propios del proyecto que no son de GameMaker (p. ej. «piedad», «bolsa aleatoria» si los usas con un sentido concreto), y un `CHANGELOG` corto del propio documento | El registro de decisiones de diseño en sí (va en el ADR ligero de `13/11 §3.5`) | Nuevo por proyecto; formato libre |

> **Las filas 2.16 (monetización) y 2.8 (meta-progresión) ya tienen documento de diseño propio.**
> Cuando se escribió esta tabla (6-sep-2026) ambas eran huecos reales de la biblioteca, señalados
> por la auditoría `_indice/auditorias/diseno-gdd.md` (I3-I6, D3-D4): la biblioteca sabía
> **implementar** la API de compras y programar un árbol de desbloqueos, pero no tenía el
> documento que enseña a **diseñar** ninguna de las dos cosas. Un día después,
> [13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md) y
> [13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md)
> cerraron los dos huecos por completo. Si tu proyecto necesita alguna de estas dos secciones, ve
> directamente a esos documentos; el criterio de diseño ya no hay que improvisarlo.

### 2.5 · Público, plataformas y competencia: el método

Esta es la única sección del cuadro de arriba que no remite a otro documento, porque la
biblioteca no la tenía resuelta (hueco A8 de la auditoría). El método es corto a propósito: para
un equipo de una a tres personas, un estudio de público completo es tiempo que no vuelve.

**Acotar el público sin inventárselo.** No se trata de escribir una *persona* de marketing con
nombre y foto de stock: se trata de responder tres preguntas con una frase cada una, y de que las
tres frases sean **verificables**, no aspiracionales:

1. **¿Quién ya juega a algo parecido?** — Nómbralos por el juego que ya juegan, no por edad o
   género demográfico: «gente que ha terminado *Celeste* en modo asistido» dice más que «18-34
   años, casual».
2. **¿Cuánto tiempo le va a dedicar de una sentada?** — Determina el bucle de sesión de
   `13/01 §2.1`, no al revés: si tu público juega en el metro, un bucle de sesión de 45 minutos
   está mal dimensionado para su plataforma, no para su gusto.
3. **¿Qué le vas a dar que la referencia no le da?** — Es la misma casilla del pitch de diseño
   (`13/01 §8.1`), pero aplicada al público en vez de al juego: si la respuesta es «nada, pero
   más barato», el público no tiene motivo para cambiar de juego.

**Qué cambia según la plataforma — decide antes de programar el input:**

| Plataforma | Sesión típica | Control | Consecuencia de diseño |
|---|---|---|---|
| PC (Steam) | Larga, con pausas | Ratón + teclado, mando opcional | El bucle de meta puede pedir más de 20 minutos; el texto en pantalla puede ser denso |
| Consola (mando) | Media | Mando siempre | Navegación con `13/05 §2.2` obligatoria desde el primer prototipo, no al final |
| Móvil táctil | Corta, interrumpible | Táctil, sin botones físicos | El bucle de sesión completo cabe en 2-5 minutos; el juego debe sobrevivir a que llamen al jugador a mitad de partida — ver [04 · 28](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) |

**El análisis de la competencia como entrada de diseño, no de marketing.** Elige de 3 a 5 juegos
de referencia y, para cada uno, escribe **una** fortaleza que vas a copiar y **una** debilidad que
vas a evitar — no una reseña. Chris Zukowski, en el consejo ya citado en
[13 · 11 §6.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#61-la-página-de-steam-es-el-primer-hito-de-marketing-no-el-último),
lo resume en tres requisitos previos a publicar la página de tienda: saber exactamente de qué
género es tu juego y **mantenerte en él**, tener decidido el estilo artístico (no terminado:
decidido) y poder enseñar profundidad con al menos tres entornos distintos. Esos tres requisitos
son, en realidad, señales de que el análisis de competencia ya se hizo bien: si no sabes en qué
género compites, tampoco sabes contra quién.

### 2.20 · El catálogo de diagramas de diseño

Un diagrama de diseño no es decoración: es la forma de que una decisión discutida en diez minutos
no se vuelva a discutir dentro de un mes. Esta biblioteca ya tiene varios, cada uno resolviendo un
problema distinto — la tabla los reúne por primera vez — y aquí se añaden los dos que faltaban
(grafo de gating y diagrama de estados) porque hoy no vivían en ningún documento.

| Diagrama | Para qué sirve | Ya existe en |
|---|---|---|
| **Bucle de cinco casillas** | Comprobar que el bucle de acción gira de verdad (la casilla [5] CAMBIO no está vacía) | [13 · 01 §2.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#22--dibujarlo-antes-de-programar) |
| **Mapa de pantallas** | Ver de un vistazo si cada pantalla tiene salida y si «Opciones» está duplicada | [13 · 05 §2.1](./05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada) |
| **Mapa de ramas narrativas** | Contar finales y recorridos, y marcar qué rama se puede cortar sin perder el acto | [13 · 12 §8.4](./12%20-%20Diseño%20narrativo%20y%20diálogos.md#84-mapa-de-ramas) |
| **Hoja / mapa de nivel** | Fijar los cuatro momentos (introducir/desarrollar/torcer/concluir) antes de abrir el Room Editor | [13 · 02 §4](./02%20-%20Diseño%20de%20niveles.md#4--la-hoja-de-nivel-la-plantilla-que-se-rellena-antes-de-construir) |
| **Diagrama de economía (fuentes/sumideros)** | Ver de dónde sale y a dónde va cada recurso antes de programarlo | Vocabulario en [13 · 01 §4.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto); la notación formal (Machinations) es un hueco — ver nota abajo |
| **Grafo de gating / dependencias** | Ver qué contenido bloquea a qué otro antes de que el `gating` de `13/01 §5.3` se vuelva espagueti | Nuevo — ver abajo |
| **Diagrama de estados del jugador** | Que cada estado tenga una salida definida, igual que las pantallas de UI | Nuevo — ver abajo |
| **Tabla de interacción entre sistemas** | Detectar acoplamientos ocultos antes de que un cambio en un sistema rompa otro en silencio | Nuevo — ver abajo |

> El diagrama de economía con la notación formal de Machinations (pool / source / drain / gate /
> converter, ver Adams y Dormans, *Game Mechanics: Advanced Game Design*, cap. 5-6) **ya tiene
> documento propio**: [13 · 21 §2.1](./21%20-%20Balance%20por%20simulación%20-%20Monte%20Carlo%2C%20Machinations%20y%20estrategias%20dominantes.md#21--diagramar-antes-de-programar-la-notación-de-machinations)
> desarrolla la notación completa (verificada contra `machinations.io/docs`) y la simulación
> Monte Carlo asociada — cuando se escribió esta tabla (6-sep-2026) era un hueco real; se cerró
> al día siguiente. La versión ASCII mínima de arriba sigue bastando para una economía pequeña
> sin convertidores; para una con varios, usa la notación formal de `13 · 21`.

**Grafo de gating / dependencias.** Un nodo por mecánica o zona, una flecha por «esto requiere
aquello». Se dibuja **antes** de decidir el orden de los niveles, no después:

```
LEYENDA   ──▶ requiere   (opcional) desbloqueo no obligatorio para terminar el juego

  [Correr y saltar] ──▶ [Agacharse] ──▶ [Cruzar el pasillo bajo de la Cripta]
        │
        └──▶ [Recoger gemas] ──(opcional)──▶ [Atajo del nivel 3]

  [Cripta superada] ──▶ [Plataforma móvil] ──▶ [Torre, sala final]
```

Si al dibujarlo aparece un ciclo (A requiere B y B requiere A), el diseño tiene un candado sin
llave: es más barato encontrarlo en el papel que en un playtest.

**Diagrama de estados del jugador.** Cada estado necesita una entrada, una salida y qué inputs
ignora mientras dura — el mismo criterio de «toda pantalla tiene salida visible» de
[13 · 05 §2.1](./05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada),
aplicado al personaje en vez de al menú:

```
   ┌────────┐  salta   ┌─────────┐  vspeed>0  ┌────────┐
   │  IDLE  │─────────▶│ SALTAR  │───────────▶│  CAER  │
   └───┬────┘          └─────────┘            └───┬────┘
       │ hspeed≠0                    toca_suelo    │
       ▼                                           ▼
   ┌────────┐                              ┌────────────┐
   │ CORRER │                              │  ATURDIDO  │ (0,4 s, ignora input)
   └────────┘                              └────────────┘
```

La utilidad no es dibujar el diagrama: es la pregunta que obliga a hacer por cada flecha «¿y si
el jugador pulsa otra cosa aquí?». Un estado sin ninguna flecha de salida (aparte de la muerte) es
un cuelgue de diseño, aunque el código nunca se cuelgue.

**Tabla de interacción entre sistemas.** Antes de programar dos sistemas que van a compartir
estado, una fila por cada par que se toca de verdad — no una matriz completa NxN, que casi
siempre está vacía y no aporta nada:

| Sistema A | Sistema B | Cómo se tocan |
|---|---|---|
| Movimiento | Cámara | La cámara sigue `x` del jugador con `lerp`; no sigue `y` salvo caída larga |
| Muerte | Checkpoints | El respawn lee la posición del último checkpoint activado, no la de la sala |
| Gemas | HUD | Cada gema recogida dispara un evento que el HUD escucha; el HUD no cuenta gemas por sí solo |

---

## 3 · Cómo se traduce a GameMaker

El documento en sí **no vive dentro del ejecutable**: vive en el repositorio, como Markdown,
igual que el resto de esta biblioteca ([§1.5](#15--wiki-viva-frente-a-documento-congelado)). Lo
que sí tiene sentido llevar dentro del propio proyecto de GameMaker es una copia de trabajo, para
que quien abre el `.yyp` — persona o agente — vea el diseño sin salir del IDE.

### 3.1 · Guardar el GDD como recurso `Notes` del proyecto

GameMaker tiene un tipo de recurso dedicado a esto: **Notes**, documentado en el manual oficial
(*El editor de notas*, `09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Notes.md`,
espejo de <https://manual.gamemaker.io/lts/es/The_Asset_Editors/Notes.htm>). El manual lo describe
como «una ventana de código/script donde podrá guardar notas […] o cualquier otra información que
considere relevante para el proyecto», agrupable y reordenable como cualquier otro asset del
[Asset Browser](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#31-el-asset-browser-por-tipo-primero-por-dominio-después).

> ⚠️ **El editor de notas es una ventana de texto plano, no un visor de Markdown.** Guardar el GDD
> ahí conserva el texto crudo (con sus `#` y sus `**`) para leerlo y hacer *grep*, versionarlo y
> tenerlo junto al código — no lo renderiza bonito dentro del IDE. Sigue siendo Markdown de verdad
> para cualquier herramienta externa (GitHub, un editor de texto, un LLM) que sí lo interprete.

### 3.2 · Crear y actualizar el `Note` con `resourcetool` (verificado en vivo)

Ni el `Note` ni ningún otro recurso se crean a mano: se hace con `gm-cli resourcetool`, la única
vía soportada (`AGENTS.md §4`). El comando `resource create` acepta `type=notes` — uno de los 17
tipos de recurso que expone la herramienta — y `NOTE SETFILEPATH` copia el contenido de un archivo
local al recurso. Los dos comandos se ejecutaron de verdad en un proyecto de prueba (`gm-cli`
`2.3.0`, `ResourceTool@2026.0.17`, `2026-09-06`) para verificar el comportamiento exacto:

```bash
# Crea el recurso Notes (queda como notes/GDD/GDD.yy dentro del proyecto)
gm-cli resourcetool eval "resource create type=notes name=GDD"

# Copia el contenido de tu documento a notes/GDD/GDD.txt
gm-cli resourcetool eval "NOTE SETFILEPATH NAME=GDD PATH=./14-el-documento-de-diseno.md"
```

> ⚠️ **Hallazgo verificado: `NOTE SETFILEPATH` no refresca el contenido de un `Note` que ya tiene
> uno asignado.** Al ejecutar el comando dos veces sobre el mismo `Note` con un archivo de origen
> modificado, la herramienta responde `Saved successfully` / `ResourceTool Successful` las dos
> veces, pero el contenido copiado en `notes/<Nombre>/<Nombre>.txt` **se queda con la primera
> versión**. La forma fiable de refrescarlo, verificada igual de en vivo, es borrar el recurso y
> volver a crearlo:
> ```bash
> gm-cli resourcetool eval "resource delete name=GDD type=notes"
> gm-cli resourcetool eval "resource create type=notes name=GDD"
> gm-cli resourcetool eval "NOTE SETFILEPATH NAME=GDD PATH=./14-el-documento-de-diseno.md"
> ```
> Esto es justo el tipo de comportamiento de herramienta que esta biblioteca existe para no
> dejarte adivinar: sin esta verificación, el `Note` del proyecto se queda silenciosamente
> desactualizado la primera vez que alguien edita el documento y vuelve a sincronizarlo.

Detalle completo del comando y del resto de `resourcetool` en
[07 · 13 §6](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md#6-gm-cli-resourcetool--editar-el-proyecto-sin-ide).

### 3.3 · Cuando el código y el documento discrepan, gana el código — con rastro

La regla ya está en [§1.5](#15--wiki-viva-frente-a-documento-congelado): gana el código en
producción, y la discrepancia se escribe como ADR ligero
([13 · 11 §3.5](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#35-registro-de-decisiones-adr-ligero)).
Lo único que añade GameMaker a esto es dónde vive el rastro dentro del propio proyecto: un ADR es
un archivo `.md` más en `decisiones/`, así que se copia al mismo `Note` (o a uno nuevo,
`notes/Decisiones/`) con el mismo comando de [§3.2](#32--crear-y-actualizar-el-note-con-resourcetool-verificado-en-vivo).
No hace falta un sistema nuevo: el mismo recurso `Notes` sirve para el GDD y para el registro de
decisiones, agrupados en una carpeta `Diseño` del Asset Browser
([13 · 06 §3.1](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#31-el-asset-browser-por-tipo-primero-por-dominio-después)).

Los **números** de balance que salen de la sección 2.9 no se guardan en el `Note`: viven en
`scr_config` o `balance.json`, exactamente como ya establece
[13 · 01 §9.2-9.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#92--scr_config--las-constantes).
El documento de diseño referencia esos parámetros por nombre (`SALTO_FUERZA`, `GRAVEDAD`); no los
duplica con un valor que se puede desincronizar del real.

### 3.4 · La plantilla completa, lista para copiar

```markdown
# <Título> · GDD completo          versión: 0.1 · fecha: AAAA-MM-DD · estado: <idea|prototipo|producción>

## 1 · Concepto y pitch
Pitch de venta:
Pitch de diseño:
Referencias (qué tomo de cada una):

## 2 · Pilares de diseño (3-5, frase afirmativa)
P1.
P2.
P3.

## 3 · Público, plataformas y competencia
A quién sirve (por el juego que ya juega, no por demografía):
Plataforma(s) y lo que eso cambia en sesión y control:
Competencia (juego → fortaleza que copio → debilidad que evito):

## 4 · Core loop
(la plantilla completa de 13/01 §8.1 va aquí, sin repetirla)

## 5 · Mecánicas, sistemas y progresión
Verbos:
Sistemas (una ficha de 13/01 §8.2 por sistema, enlazadas o adjuntas):
Progresión y dificultad:

## 6 · Economía y balance
(vocabulario y fórmulas de 13/01 §4, con los números reales)

## 7 · Niveles y mundo
(una hoja de nivel de 13/02 §4 por nivel, enlazadas o adjuntas)

## 8 · Personajes y narrativa
(biblia de 13/12 §8.1 y fichas de personaje de 13/12 §8.2)

## 9 · Arte, audio y UI
Dirección visual:
Dirección de sonido:
Mapa de pantallas:

## 9 bis · Envoltorio de pantallas       (fila 2.14 bis; checklist maestro en 04/00)
Splash:                    presente | no aplica: <razón>
Menú principal:             presente | no aplica: <razón>
Selección de nivel/capítulo: presente | no aplica: <razón>   (04/57, si el juego tiene niveles discretos)
Pausa:                      presente | no aplica: <razón>
Opciones:                   presente | no aplica: <razón>
Créditos:                   presente | no aplica: <razón>

## 10 · Técnica
Motor de físicas, formato de datos, dónde vive el estado:

## 11 · Monetización        (criterio de diseño en 13/20, ver §2 fila 2.16)
## 12 · Marketing y lanzamiento
(remite a 13/11 §6 y a la plantilla de press kit de §8.4)

## 13 · Calendario y alcance
(remite a 13/11 §1-§3; matriz de recorte y fases)

## 14 · Anexos
Glosario del proyecto:
Registro de cambios de este documento:

## 15 · Checklist de cierre
(una casilla por criterio de aceptación de cada ficha de la sección 5 — copiado de su «Cómo se
 prueba», `13 · 01 §8.2` — más las filas del envoltorio de pantallas de la sección 9 bis y, si
 el juego va a publicarse, el checklist completo de
 [04 · 00](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md).
 Vacía hasta que existan sistemas fichados; se rellena a medida que la sección 5 crece, no al
 final. La tarea no está cerrada hasta que cada casilla se cumple Y `gm-cli compile` sale limpio)
- [ ] <sistema> — <criterio de aceptación tal cual, no una versión relajada>
```

---

## 4 · Checklist

**Antes de decidir que hace falta un GDD completo**

- [ ] Al menos una de las cuatro señales de [§1.1](#11--cuándo-el-one-pager-no-basta) aplica de
      verdad, y no es solo la costumbre de «un proyecto serio necesita un documento grande»
- [ ] El GDD de una página de `13/01 §8.1` ya existe: el completo se **expande** desde ahí, no
      se escribe desde cero

**Antes de dar el documento por listo**

- [ ] Cada una de las 20 secciones de [§2](#2--el-método-paso-a-paso) tiene contenido o dice
      explícitamente **por qué no aplica** a este proyecto (una sección vacía sin explicación es
      indistinguible de un olvido) — incluida **2.14 bis, el envoltorio**: splash, menú, pausa,
      opciones y créditos marcados uno a uno, no asumidos
- [ ] Los pilares son 3-5, están en frase afirmativa, y al menos uno ha rechazado una idea real
- [ ] El pitch de venta y el de diseño son textos **distintos**, no el mismo copiado dos veces
- [ ] Ningún número de balance está escrito dos veces (documento y `balance.json`): el documento
      referencia el nombre del parámetro, no un valor que se puede desincronizar
- [ ] Los diagramas que aplican a tu proyecto están dibujados, aunque sea en ASCII: bucle,
      mapa de pantallas, y — si hay contenido que se desbloquea — el grafo de gating

**Antes de que un LLM lo implemente**

- [ ] Cada sistema tiene reglas **numeradas y en imperativo**, no descritas en prosa
- [ ] Cada parámetro de balance tiene un **rango**, no solo un valor («la fuerza de salto está
      entre 9 y 13, empieza en 11» es implementable; «un salto que se sienta bien» no lo es)
- [ ] El recorte (qué NO está en el juego) está **escrito**, no asumido
- [ ] Hay un criterio de aceptación por el que el agente sabe cuándo parar de iterar
- [ ] La sección 15 (checklist de cierre) tiene una casilla por cada criterio de aceptación de la
      sección 5 — el documento es autocontenido, no depende de que el agente vuelva a este §4

**Para mantenerlo vivo**

- [ ] Hay un ADR ligero por cada decisión cara de revertir que se tomó **distinto** de lo que
      decía el documento
- [ ] La fecha de «última revisión» de cada sección no tiene más de un ciclo de desarrollo

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo se evita |
|---|---|---|
| **Escribir el GDD completo antes del one-pager** | Parece más «serio» empezar grande | El one-pager de `13/01 §8.1` primero, siempre; el completo es una expansión, no un punto de partida |
| **Pilares que son listas de características** | Es más fácil listar lo que tiene el juego que decidir qué experiencia produce | Cada pilar debe poder **rechazar** una idea real; si no rechaza nada, no es un pilar |
| **Confundir pitch de venta con pitch de diseño** | Solo se escribe una frase y se reutiliza para todo | La tabla de [§1.4](#14--el-elevator-pitch-fórmula-qué-no-lleva-venta-frente-a-diseño): dos textos, dos públicos |
| **El documento se convierte en el trabajo** | Media tarde maquetando tablas bonitas es media tarde sin tocar el juego | La regla de `13/11 §3.7`: la herramienta no es el trabajo |
| **Duplicar números entre el GDD y `balance.json`** | Se escribe el valor directamente porque es más rápido | Referenciar el **nombre** del parámetro (`SALTO_FUERZA`), nunca copiar el valor |
| **Una sección vacía sin decir por qué** | Se deja «para luego» y se olvida | Si no aplica, se escribe «No aplica: <razón>» — una línea, no un silencio |
| **El documento describe el juego que se quiere hacer, no el que se está haciendo** | Nadie actualiza el documento cuando el código cambia de idea | ADR ligero en el mismo commit que el cambio (`13/11 §3.5`); ver [§1.5](#15--wiki-viva-frente-a-documento-congelado) |
| **Pedirle a un LLM que implemente desde un GDD «bonito» pero ambiguo** | El documento se escribió para que lo lea una persona, con huecos que un compañero rellenaría preguntando | La versión para LLM de [§6](#6--la-versión-para-llm-qué-necesita-un-agente-para-implementar-sin-inventar): reglas numeradas, rangos, recorte explícito |
| **Actualizar el `Note` del proyecto y que se quede con el contenido viejo** | `NOTE SETFILEPATH` no refresca un `Note` que ya tiene archivo asignado (verificado en [§3.2](#32--crear-y-actualizar-el-note-con-resourcetool-verificado-en-vivo)) | Borra el recurso y vuelve a crearlo en vez de repetir `SETFILEPATH` sobre el mismo `Note` |
| **Inventar una plantilla para una sección que no tiene documento propio en la biblioteca** | Se asume que toda sección del cuadro de §2 tiene equivalente en otro documento sin comprobarlo | Sigue el enlace de la columna «Dónde está desarrollado» de §2; si de verdad no hay documento (compruébalo con `buscar.py --texto`), marca ⚠️ la sección y decide con criterio propio en vez de inventar una plantilla. Monetización y meta-progresión, que eran el ejemplo clásico de este error, ya tienen documento propio en [13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md) y [13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md) |

---

## 6 · La versión para LLM: qué necesita un agente para implementar sin inventar

### 6.1 · Qué hace que un GDD sea «implementable» y no solo «leíble»

Un GDD escrito para un compañero humano puede permitirse ambigüedad porque un humano la resuelve
**preguntando**: «¿cuánto debería tardar el salto en llegar arriba?» tiene una respuesta que se da
en el pasillo en diez segundos. Un agente no pregunta por defecto — cuando la respuesta falta,
**inventa una firma, un número o una regla que suena plausible**, que es exactamente el fallo que
esta biblioteca entera existe para evitar (`AGENTS.md §1`). La diferencia entre un GDD para
persona y uno para agente no es de formato: es de **dónde se traslada la ambigüedad**. Cinco
condiciones, en orden de coste si faltan:

1. **Reglas numeradas y en imperativo**, no prosa. «El salto se siente ágil» no es implementable;
   «`R1. vspeed = -SALTO_FUERZA` en el frame en que se detecta el input» sí lo es, exista o no
   todavía el código.
2. **Cada parámetro con un rango, no solo un valor inicial** — la tabla de balance de
   `13/01 §8.2` ya lo pide; para un agente es la diferencia entre «prueba con 11» y «prueba con
   cualquier número entre 9 y 13 y decide con el playtest».
3. **El recorte explícito, en la misma jerarquía que las reglas.** Un agente que no sabe que
   «no hay doble salto» va a intentar hacer el juego más completo por iniciativa propia, porque
   nadie le dijo que eso restaba en vez de sumar.
4. **Un criterio de aceptación que no dependa de una opinión.** «Que se sienta bien» no cierra una
   tarea; «los 3 niveles compilan y las 3 gemas de cada uno son recogibles» sí.
5. **Lo que no está decidido se señala como pregunta abierta, nunca se implementa por iniciativa
   propia.** Si una regla es ambigua, un parámetro no tiene rango, o el usuario pide algo que el
   recorte del punto 3 ya excluyó, el agente lo dice y espera respuesta — no rellena el hueco con
   la opción que le parece razonable. Es la regla que ya aplicaba el recorte de
   [§6.3 punto 9](#63--ejemplo-real-un-plataformas-de-3-niveles), generalizada aquí: gobierna
   cualquier ambigüedad de esta sección, no solo el recorte. El protocolo para llegar hasta este
   punto —qué preguntar antes de escribir la primera versión del documento, cuándo parar de
   preguntar y qué asumir por defecto— es
   [13 · 28](./28%20-%20De%20hazme%20un%20juego%20a%20una%20especificación%20-%20el%20protocolo%20de%20elicitación%20del%20agente.md#16--lo-que-no-está-decidido-se-señala-como-pregunta-abierta-nunca-se-implementa-por-iniciativa-propia).

Esto no sustituye la verificación de símbolos GML que exige `AGENTS.md §1` (`buscar.py` antes de
escribir cualquier función): un GDD perfecto no libra al agente de comprobar que `place_meeting`
existe. Lo que sí evita es que el agente tenga que **adivinar la intención de diseño** mientras
además verifica la API — son dos fuentes de invención distintas, y esta sección resuelve solo
la primera.

### 6.2 · La plantilla mínima para LLM

Es la ficha por sistema de `13/01 §8.2` con tres campos añadidos, pensados específicamente para
que el agente no tenga que decidir nada que no sea puramente de implementación:

```markdown
# Sistema: <nombre>                     estado: por implementar · implementado · balanceado

**Para qué existe:** (en términos del pilar al que sirve, no de la mecánica)
**Reglas:** numeradas, en imperativo, comprobables — R1, R2…
**Parámetros de balance:** nombre · valor inicial · RANGO · dónde vive (balance.json)
**Casos borde:** qué pasa en los extremos, no solo en el caso normal
**Símbolos GML que probablemente hagan falta:** los que el redactor del GDD ya intuye — el
  agente los verifica igualmente con `buscar.py` antes de usarlos; esta lista solo ahorra
  una búsqueda a ciegas, no sustituye la verificación
**Fuera de alcance para este sistema:** lo que un agente «servicial» tendería a añadir y no debe
```

### 6.3 · Ejemplo real: un plataformas de 3 niveles

El siguiente documento está completo tal y como se le entregaría a un agente implementador — no
es un fragmento. Cada función y variable de GameMaker que nombra está verificada contra
`_indice/simbolos.json` con `buscar.py` antes de escribirla aquí.

```markdown
# Luz de Ámbar · GDD para agente implementador     versión: 1.0 · fecha: 2026-09-06

## 0 · Metadatos
Género: plataformas 2D. Motor: GameMaker LTS 2026.0. Alcance: 3 niveles, ~15 min de recorrido.
Estado: congelado para esta implementación (ver §1.5 de 13/14 sobre wiki viva).

## 1 · Pitch y pilares
Pitch: una luciérnaga cruza tres ruinas antes de que se apague la última antorcha.
P1. El salto es el único verbo de combate: no hay ataque, solo esquiva y sincronización.
P2. Cada muerte es instantánea y el respawn es inmediato (< 0,5 s): no hay pantalla de carga.
P3. La luz es un recurso visible que se agota: nunca hay temporizador invisible al jugador.

## 2 · Público y plataforma
PC, teclado. Sesión de 12-18 min. Dificultad de jugador ocasional de plataformas (referencia:
Celeste en modo asistido, sin exigir su precisión de pixel perfecto).

## 3 · Bucle
Acción (segundos): correr y saltar → para esquivar una trampa → que permite llegar a la antorcha.
Sesión (minutos): recorrer un nivel entero → para conseguir 3 gemas → que abren el atajo siguiente.
Meta: no aplica. Es un arcade de 3 niveles sin progresión permanente — decisión explícita.

## 4 · Verbos (máximo 5)
Correr · Saltar (un único salto, sin doble salto) · Agacharse (reduce el alto de la hitbox)

## 5 · Sistema: Movimiento y salto                    estado: por implementar
Para qué existe: sostiene P1 — el salto debe sentirse preciso y perdonar el borde del suelo.
Reglas:
  R1. Al detectar `keyboard_check_pressed(vk_space)` con el jugador en el suelo o dentro de la
      ventana de coyote time (R2), fijar `vspeed = -SALTO_FUERZA` una sola vez por pulsación.
  R2. Coyote time: 6 frames tras dejar el suelo en los que el salto sigue siendo válido, contados
      con `alarm[0]`.
  R3. Gravedad: sumar `GRAVEDAD` a `vspeed` cada Step, con tope en `VSPEED_MAX` (la caída no
      acelera sin límite).
  R4. Suelo: `place_meeting(x, y+1, obj_solido)` decide si se puede saltar y si `vspeed` se
      resetea a 0 al aterrizar.
Parámetros de balance:
| Nombre | Valor inicial | Rango | Dónde vive |
|---|---|---|---|
| SALTO_FUERZA | 11 | 9 a 13 | balance.json |
| GRAVEDAD | 0.55 | 0.4 a 0.7 | balance.json |
| VSPEED_MAX | 12 | 10 a 16 | balance.json |
| COYOTE_FRAMES | 6 | 4 a 10 | balance.json |
Casos borde: un salto pulsado hasta 4 frames antes de tocar el suelo cuenta (input buffer) ·
aterrizar sobre un peligro mata en el mismo frame en que se detecta, no en el siguiente.
Símbolos GML probables: keyboard_check_pressed, vk_space, place_meeting, vspeed, alarm.
Fuera de alcance: doble salto, salto variable por tiempo de pulsación, dash.

## 6 · Sistema: Muerte y respawn                      estado: por implementar
Para qué existe: sostiene P2.
Reglas:
  R1. Al tocar `obj_peligro`, destruir al jugador con `instance_destroy` y recrearlo con
      `instance_create_layer` en la posición del último checkpoint activado (no reiniciar la
      sala: reiniciarla perdería las gemas ya recogidas).
  R2. El respawn tarda menos de 0,5 s en dar control al jugador; no hay pantalla de carga.
Casos borde: morir dentro del área de un checkpoint no debe reactivarlo dos veces.
Símbolos GML probables: instance_destroy, instance_create_layer.
Fuera de alcance: vidas limitadas, penalización de gemas al morir.

## 7 · Sistema: Gemas y HUD                           estado: por implementar
Para qué existe: sostiene el bucle de sesión (§3) y da feedback visible de progreso (P3).
Reglas:
  R1. Cada nivel tiene 3 gemas; ninguna es obligatoria para terminarlo.
  R2. El HUD dibuja `gemas_recogidas / 3` en la esquina superior izquierda, en la GUI Layer.
Parámetros: GEMAS_POR_NIVEL = 3 (fijo: es una decisión de diseño, no un ajuste de balance).
Símbolos GML probables: draw_sprite, sprite_index, image_xscale.
Fuera de alcance: inventario, gemas que se puedan gastar.

## 8 · Niveles (hoja abreviada — plantilla completa en 13/02 §4)
| Nivel | Idea en una frase | Métrica clave | Elemento nuevo |
|---|---|---|---|
| 1 · Atrio | Enseña salto y coyote time sin riesgo de muerte | Alcance máx. 4 celdas | — |
| 2 · Cripta | Introduce obj_peligro y el primer checkpoint | Obstáculo máx. 2 celdas | Pinchos |
| 3 · Torre | Combina salto + una gema arriesgada antes del final | Abismo máx. 5 celdas | Plataforma móvil |

## 9 · Recorte explícito
NO hay en este proyecto: enemigos con IA, doble salto, mundo abierto, guardado entre sesiones,
menú de opciones más allá del volumen. Si el agente considera necesario añadir algo de esta
lista, debe señalarlo como pregunta abierta, no implementarlo por iniciativa propia.

## 10 · Criterio de aceptación
La tarea se da por terminada cuando: los 3 niveles compilan con `gm-cli compile` sin errores, el
salto cumple R1-R4 de §5, morir siempre respawnea en el último checkpoint (o en el inicio del
nivel si no se activó ninguno), y las 3 gemas de cada nivel son recogibles y suman en el HUD.
```

Ese documento son 83 líneas y contiene todo lo que la sección 6.1 pedía: reglas numeradas, rangos
en cada parámetro, recorte explícito y un criterio de aceptación verificable. No contiene el
código GML en sí — eso lo escribe el agente, verificando cada símbolo con `buscar.py` como exige
`AGENTS.md`, con la ventaja de que ya no tiene que **además** adivinar qué se le estaba pidiendo.

### 6.4 · Cómo lo usaría un agente, paso a paso

1. Lee el documento entero antes de tocar el IDE — igual que pide `AGENTS.md` con esta biblioteca.
2. Por cada sistema, verifica los símbolos de la lista «probables» con
   `python3 "_indice/buscar.py" <símbolo>` — la lista ahorra una búsqueda a ciegas, no la
   sustituye: puede haber cambiado de nombre o estar obsoleta desde que se escribió el documento.
3. Crea los objetos y eventos con `gm-cli resourcetool` (`AGENTS.md §4`), nunca a mano.
4. Escribe el `.gml` de cada regla, una por una, comprobando después de cada sistema con
   `gm-cli compile` en vez de esperar a tener los tres niveles enteros para compilar por primera
   vez — el mismo criterio de iteración rápida de `13/01 §8.3`.
5. Al terminar, compara contra el **criterio de aceptación** de la sección 10, no contra una
   sensación de «está bien»: si algo de la lista no se cumple, la tarea no está terminada.
6. Si el agente detecta que una regla es ambigua o que faltan datos, **lo dice** en vez de rellenar
   el hueco con una suposición razonable — es la misma regla de no-improvisación de las
   instrucciones de sesión que gobiernan este documento.
7. **Repórtalo al usuario** — al terminar el primer sistema jugable (no esperes a tener los tres)
   y de nuevo al cerrar la sesión. `AGENTS.md` línea 186 ya exige reportar la salida real de
   `gm-cli compile`; falta la mitad simétrica: reportar el alcance real frente al prometido. La
   plantilla corta, siempre con estos cuatro bloques:

   ```markdown
   ## Reporte de sesión — <fecha>
   **Se construyó**: <cada sección de sistema (§5 en adelante en el ejemplo de §6.3) cuyo
     campo "estado" quedó en "implementado", uno por línea>
   **Quedó en el recorte**: <lo de la sección 9 que no se tocó, y por qué — falta de tiempo,
     dependía de una pregunta abierta, o se decidió que no cabía en el alcance de la sesión>
   **Preguntas abiertas**: <si el punto 6 se disparó en algún sistema, o §1.6 en la elicitación,
     la pregunta exacta y qué falta para cerrarla — vacío si no hubo ninguna>
   **`gm-cli compile`**: <salida real, no un «compila bien» sin más>
   ```

   Si un criterio de aceptación de la sección 10 resulta **inalcanzable** (una plataforma sin
   soporte, una función que `buscar.py` marca obsoleta y no tiene sustituto directo), no se
   omite ni se relaja en silencio: se anota como pregunta abierta en el reporte con el motivo
   verificado, igual que cualquier otra ambigüedad del punto 6 — la sección 10 se queda como
   estaba escrita, y es el reporte el que dice que ese criterio concreto no se cumplió, no el GDD
   el que se reescribe a la baja para que cuadre.

---

## 7 · Del GDD al proyecto: la lista de tareas y el árbol de recursos

El §6 resuelve **un** sistema aislado a la perfección: con la plantilla mínima y el ejemplo de
«Luz de Ámbar», un agente sabe implementar «Movimiento y salto» sin inventar nada. Lo que ese
ejemplo no responde —porque un GDD de tres sistemas no lo necesita, y uno de quince sí— son dos
preguntas que aparecen en cuanto el documento crece: **¿en qué orden se construyen los sistemas
de la ficha?** y **¿qué recursos concretos de GameMaker derivan de cada campo de una ficha ya
escrita?** `13 · 18 §4.1` ya contesta la segunda pregunta, pero **solo para combate**; esta
sección generaliza ese mismo patrón a cualquier sistema de `13 · 01 §8.2`, y añade la pieza que
falta del todo: el orden entre sistemas y el paso de la ficha al tablero de `13 · 11 §3.1`.

### 7.1 · De cualquier ficha de sistema a los recursos de GameMaker

La ficha de `13 · 01 §8.2` tiene ocho campos. Cada uno apunta a un tipo de recurso distinto —la
tabla es el mismo ejercicio que `13 · 18 §4.1` hizo para combate, aplicado a los ocho campos en
vez de a una lista de sistemas concretos:

| Campo de la ficha (`13 · 01 §8.2`) | Qué recurso de GameMaker deriva | Regla para decidir |
|---|---|---|
| **Para qué existe** | Ninguno directamente — es la prueba con la que se descarta un sistema entero antes de crear nada (§1.3 de este documento, la pregunta «¿sirve al pilar?») | — |
| **Entradas** | Normalmente ninguno nuevo: casi siempre es otro sistema ya construido, o `keyboard_check`/`gamepad_*` | Si la entrada no existe todavía como sistema, es una **dependencia**: va antes en el orden de §7.2 |
| **Salidas** | Un evento de [04 · 16 — Señales](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md) si otros sistemas lo consumen sin acoplarse; una variable directa si solo lo lee un objeto concreto | Más de un sistema escuchando → señal. Uno solo, siempre el mismo → variable de instancia |
| **Estado que mantiene** | `obj_*` nuevo con variables de instancia (estado **por entidad**: vida, posición, temporizador propio) · `scr_*` + struct en `global.*` (estado **compartido**: inventario, progreso de nivel) · `balance.json`/archivo (estado que sobrevive a cerrar el juego) | La pregunta que decide: ¿existe más de una instancia con este estado a la vez? Si sí, `obj_`. Si es uno solo para todo el juego, `global.*` |
| **Reglas numeradas R1-Rn** | El `.gml` real: casi siempre un evento (`Create`/`Step`/`Collision`) del `obj_` de la fila de arriba, o una función en un `scr_` si no hay estado por instancia | Una regla que empieza por «al detectar X…» casi siempre es un evento; una que empieza por «calcular Y a partir de…» casi siempre es una función pura en un `scr_` |
| **Parámetros de balance** | `#macro` en `scr_config` si no va a tocarse en caliente; entrada en `balance.json` si sí (criterio completo en [13 · 01 §9.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#91--dónde-vive-cada-decisión-de-diseño), no se repite aquí) | — |
| **Interacciones con otros sistemas** | Nada nuevo por sí solo — es la fila que rellena la **tabla de interacción entre sistemas** de [§2.20](#220--el-catálogo-de-diagramas-de-diseño), la entrada de §7.2 | — |
| **Feedback al jugador** | `spr_*`/`snd_*` nuevos, o una entrada más en el catálogo de VFX ya existente ([04 · 39](../04%20-%20Recetas%20por%20género/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md)) | Antes de pedir un asset nuevo, comprueba si el catálogo de `04 · 39` ya resuelve el efecto |
| **Casos borde** | Ninguno — no generan recurso, generan **tarea de verificación** en el tablero (§7.3) | — |
| **Cómo se prueba** | Ninguno — es el criterio de aceptación de la tarjeta de tablero que cierra el sistema (§7.3) | — |
| **Telemetría** | Una llamada a `telemetria_registrar()` ([13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json)), nunca un sistema de registro propio | — |

> 💡 **`obj_` nuevo frente a extender uno que ya existe.** La tabla de arriba dice cuándo hace
> falta un objeto, pero no distingue «uno nuevo» de «una variable más en el `obj_jugador` que ya
> tienes» — esa es la pregunta de composición de
> [13 · 06 §3.6](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#36-composición-frente-a-herencia),
> y esta sección no la repite: la ficha de sistema te dice **que** hace falta estado nuevo; ese
> otro documento te dice **dónde** debe vivir dentro de la jerarquía de objetos que ya tienes.

**Antes de crear nada, verifica que no exista.** El mapa de decisión de `AGENTS.md §2` («¿qué
librería/extensión existe para X?») aplica con más fuerza aquí que en ningún otro sitio: antes de
crear un `obj_` para el sistema nuevo, `python3 "_indice/buscar.py" --texto "<el sistema>"` —
puede que ya exista una receta entera en `04 - Recetas por género/` que resuelva ese sistema de
la ficha sin escribir una línea.

### 7.2 · El orden entre sistemas de un GDD completo

`13 · 06 §2` ya da el orden de **montaje del esqueleto vacío** (Git, `scr_config`, `obj_game`,
guardado con versión) — eso pasa **una vez**, al principio del proyecto, antes de que exista
ningún sistema de diseño. Esta sección es la pieza siguiente: dado un GDD con quince sistemas ya
fichados (`13 · 01 §8.2` por cada uno), **¿en qué orden se implementan?**

**El método es el mismo que ya usa `13 · 14 §2.20` para detectar acoplamientos, aplicado a la
pregunta de secuencia en vez de a la de riesgo.** Rellena la tabla de interacción entre sistemas
—una fila por cada par que se toca de verdad, no una matriz NxN vacía— y lee las flechas como un
grafo de dependencia: si el campo «Entradas» de un sistema B nombra algo que produce el sistema
A, hay una arista `A → B`, y A va antes. Es exactamente el mismo ejercicio que el **grafo de
gating** de `§2.20` aplicado a sistemas de código en vez de a mecánicas de contenido — y si al
dibujarlo aparece un ciclo (A necesita a B y B necesita a A), el diseño tiene un problema real
que es mucho más barato encontrar en esta tabla que a mitad de implementar los dos.

Sin necesidad de dibujar el grafo cada vez, la dependencia real entre **tipos** de sistema sigue
casi siempre el mismo orden, porque son las mismas categorías las que producen las entradas de
las demás en cualquier proyecto:

| Orden | Categoría de sistema | Por qué va ahí, no antes ni después |
|---|---|---|
| 1 | **Núcleo de movimiento y colisión** | Todo lo demás lee `x`/`y` o un estado derivado de ellas — es la única categoría sin ninguna entrada que dependa de otro sistema de diseño |
| 2 | **Cámara** | Necesita la posición del jugador del paso 1 para seguir algo; no tiene sentido antes |
| 3 | **El sistema que sostiene el pilar principal** | Es la razón de ser del juego (§1.3): si el pilar es «el salto preciso», es el propio movimiento del paso 1; si es «el sigilo», es aquí donde entra la percepción de `04 · 31`/`04 · 45` |
| 4 | **Combate/enemigos, si el juego lo tiene** | Necesita el movimiento (para golpear algo que se mueve) y a menudo la cámara (para encuadrar el combate); casi nunca lo necesita nadie de los pasos 1-3 |
| 5 | **UI/HUD** | Por definición **muestra** el estado de otro sistema (vida, munición, gemas) — construirlo antes es adivinar qué campos va a necesitar leer |
| 6 | **Guardado** | Necesita que exista estado real que guardar; guardarlo antes de tenerlo es guardar structs vacíos que habrá que migrar en cuanto cambien (`13 · 06 §3.10`) |
| 7 | **Audio** | Reacciona a eventos que los sistemas anteriores ya disparan (golpe, salto, gema recogida) — construirlo antes es adivinar qué eventos van a existir |
| 8 | **Pulido** (*juice*, [04 · 15](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md)) | Por construcción, pulir es la última capa sobre sistemas que ya funcionan — pulir algo que todavía va a cambiar es trabajo que se tira |

> ⚠️ **Esta tabla es el orden por defecto, no una ley.** Si la tabla de interacción entre
> sistemas de tu GDD concreto muestra una dependencia distinta —un HUD que necesita existir antes
> que el combate porque el combate lo consulta para saber si mostrar un aviso, por ejemplo—, gana
> la tabla de interacción real, no esta lista genérica. La lista sirve para el 90 % de los
> proyectos que no tienen una razón concreta para desviarse, y para dar un punto de partida
> cuando construir la tabla completa de `§2.20` sería desproporcionado para un GDD pequeño.

**Ejemplo, sobre el mismo GDD de `§6.3`.** «Luz de Ámbar» tiene tres sistemas fichados:
Movimiento y salto, Muerte y respawn, Gemas y HUD. La tabla de interacción entre sistemas de
`§2.20` ya los cruza: *Movimiento → Cámara* (no fichada aparte: es la del propio `04 · 01`),
*Muerte → Checkpoints* (el respawn lee la posición del checkpoint, no al revés) y *Gemas → HUD*
(el HUD escucha, no cuenta por sí solo). Aplicando la tabla de categorías de arriba: **Movimiento
y salto** (categoría 1, y además el pilar principal — categorías 1 y 3 coinciden porque P1 de
ese GDD *es* el salto) primero; **Muerte y respawn** después, porque depende de que el jugador
pueda ya moverse y colisionar con `obj_peligro`; **Gemas y HUD** al final, porque el HUD necesita
que exista algo que mostrar (gemas ya recogibles) antes de dibujar su contador — el mismo orden
en que el propio documento de `§6.3` los numeró (§5, §6, §7), que no fue casualidad: se escribió
ya siguiendo esta regla.

### 7.3 · De cada fila de la ficha a las tarjetas del tablero

El puente final: `13 · 11 §3.2` pide tareas de un día, con la tabla de ejemplo «Hacer el sistema
de combate» → seis tarjetas. Esa tabla no explica **de dónde** salen esas seis tarjetas; salen,
sistemáticamente, de la misma ficha de `§8.2` que ya escribiste para ese sistema:

| Campo de la ficha | Se convierte en… |
|---|---|
| Cada regla `R1…Rn` | Una tarjeta, o el núcleo de una — una regla compleja (```R1``` con varias condiciones) puede partirse en 2-3 tarjetas si no cabe en un día |
| **Feedback al jugador** | Una tarjeta aparte, casi siempre la última del sistema — necesita que la mecánica ya funcione para saber cómo se ve/suena de verdad |
| Cada **caso borde** listado | Una tarjeta de verificación propia, no una nota al margen de otra tarjeta — si no tiene su propia tarjeta, se olvida |
| **Cómo se prueba** | No es una tarjeta: es el criterio de aceptación que cierra **todas** las tarjetas del sistema — la misma función que el criterio de aceptación de `§6.3` para un agente, aplicada a una persona con el tablero |

Aplicado a «Movimiento y salto» de `§6.3` (R1-R4, un caso borde de *input buffer* y uno de morir
al aterrizar sobre un peligro):

| Backlog (extracto) |
|---|
| Salto con coyote time (R1, R2) |
| Gravedad con tope de velocidad (R3) |
| Detección de suelo y reseteo de `vspeed` (R4) |
| Input buffer: salto pulsado hasta 4 frames antes de tocar suelo |
| Aterrizar sobre `obj_peligro` mata en el mismo frame, no en el siguiente |
| Squash & stretch del salto (feedback, `04 · 15`) |

Seis tarjetas de un GDD de 15 líneas para un solo sistema — la misma densidad que ya mostraba el
ejemplo de `13 · 11 §3.2` para combate, ahora con la trazabilidad explícita de qué campo de qué
ficha produjo cada una. El sistema se da por **terminado** cuando las seis están en «Hecho» **y**
se cumple «Cómo se prueba» de la ficha — no antes, y no con menos.

---

## Ver también

- [13 · 01 — Diseño de juego](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) — el GDD de una página y la ficha por sistema que este documento no repite (§8); MDA, bucle, economía y balance que alimentan los pilares y las secciones 2.5-2.9
- [13 · 02 — Diseño de niveles](./02%20-%20Diseño%20de%20niveles.md) — la hoja de nivel que rellena la sección 2.10 y el ejemplo de §6.3
- [13 · 03 — Pixel art y resolución](./03%20-%20Pixel%20art%20y%20resolución.md) · [13 · 04 — Animación](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md) — lo que llena la sección 2.12
- [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md) — el mapa de pantallas del catálogo de diagramas (§2.20) y la sección 2.14
- [13 · 06 — Arquitectura de un proyecto GameMaker](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — el Asset Browser donde vive la carpeta `Diseño` de §3.3, la sección técnica 2.15, el orden de montaje del esqueleto vacío (§2) y composición frente a herencia (§3.6) que §7.1-7.2 usan sin repetir
- [13 · 09 — Diseño de sonido y mezcla](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) — la sección 2.13
- [13 · 11 — Producción, alcance y lanzamiento](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) — ADR ligero y diario de desarrollo (§1.5, §3.3), herramientas de wiki viva, calendario y alcance (2.18), lanzamiento y press kit (2.17), el tablero de cuatro columnas y las tareas de un día (§3.1-3.2) que §7.3 convierte en tarjetas concretas
- [13 · 18 — Diseño de combate y de jefes](./18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md) §4.1 — el patrón «campo de la ficha → recurso de GameMaker», aplicado a combate; §7.1 lo generaliza a cualquier sistema
- [13 · 12 — Diseño narrativo y diálogos](./12%20-%20Diseño%20narrativo%20y%20diálogos.md) — biblia del mundo, fichas de personaje y mapa de ramas de la sección 2.11 y del catálogo de diagramas
- [13 · 20 — Modelo de negocio, monetización y ética del diseño](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md) — el criterio de diseño de la sección 2.16
- [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md) — el criterio de diseño de la meta-progresión de la sección 2.8
- [04 · 20 — Servicios de plataforma](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md) — la implementación a la que remite la sección 2.16
- [04 · 28 — Juegos para móvil (táctil)](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) — lo que cambia el diseño en la fila «móvil» de §2.5
- [07 · 13 — GM CLI, la línea de comandos](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md) — `resourcetool`, los 17 tipos de recurso y el comando `NOTE SETFILEPATH` verificado en §3.2
- [09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Notes.md](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Notes.md) — el editor de notas, fuente oficial de §3.1
- [_indice/auditorias/diseno-gdd.md](../_indice/auditorias/diseno-gdd.md) — la auditoría que encarga este documento y señala los huecos (monetización, meta-progresión, teoría más allá de MDA) que aquí se marcan con ⚠️ en vez de rellenarse sin fuente
- [AGENTS.md](../AGENTS.md) — la regla de no inventar símbolos de GML que gobierna toda la sección 6

---

## Fuentes

Todas consultadas y reverificadas en vivo el **2026-09-06**.

**El documento de diseño y su historia**

- Tim Ryan — *The Anatomy of a Design Document, Part 1: Documentation Guidelines for the Game
  Concept and Proposal*, Gamasutra, 19 de octubre de 1999 —
  <https://www.gamedeveloper.com/design/the-anatomy-of-a-design-document-part-1-documentation-guidelines-for-the-game-concept-and-proposal> ·
  200 OK hoy · la cita de la documentación como «biblia» del productor y guía de implementación
  para programadores y artistas, y la estructura en dos etapas (concepto → propuesta) que este
  documento reordena para un equipo pequeño en vez de copiar
- Tracy Fullerton — *Game Design Workshop: A Playcentric Approach to Creating Innovative Games* —
  capítulo de *pitching* (distinción entre pitch de venta y pitch de diseño interno) y capítulo
  de documentación (práctica de wiki de equipo). Libro, sin URL — ya citado con el mismo alcance
  en `13/01` y `13/11` de esta biblioteca

**Pilares de diseño**

- Max Pears — *Design Pillars: The Core of Your Game*, Game Developer, 12 de octubre de 2017 —
  <https://www.gamedeveloper.com/design/design-pillars-the-core-of-your-game> · 200 OK hoy ·
  definición de 3-5 pilares, la pregunta «¿sirve a los pilares?» como filtro de diseño, y los
  ejemplos de *The Last of Us* y *Breath of the Wild*

**El pitch**

- Alex Nichiporchik — *How To Pitch Your Game*, Game Developer, 17 de septiembre de 2015 —
  <https://www.gamedeveloper.com/business/how-to-pitch-your-game> · 200 OK hoy · qué SÍ y qué NO
  lleva un elevator pitch de videojuego, y la práctica de «practica tu respuesta en voz alta»
- Gamestorming — *Elevator Pitch* — <https://gamestorming.com/elevator-pitch/> · la fórmula
  «X se encuentra con Y, en Z» y el ejemplo de *Viva Piñata: Party Animals*

**Wiki viva frente a documento congelado**

- Nuclino — *How to Write a Game Design Document (GDD)*, actualizado el 12 de enero de 2026 —
  <https://www.nuclino.com/articles/write-game-design-document> · 200 OK hoy · la cita de Rodolfo
  Rubens sobre los documentos de diseño «muy vivos», y el riesgo simétrico de tratar el GDD como
  plano rígido

**GameMaker**

- Manual oficial LTS — *El editor de notas* —
  <https://manual.gamemaker.io/lts/es/The_Asset_Editors/Notes.htm> (espejo local en
  `09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Notes.md`) · el recurso `Notes` como
  ventana de código/script, agrupable en el Asset Browser
- `gm-cli` `2.3.0` / `ResourceTool@2026.0.17` — comportamiento de `resource create type=notes` y
  `NOTE SETFILEPATH` verificado ejecutando los comandos de verdad en un proyecto de prueba
  (plantilla *Blank Pixel Game*) el 2026-09-06, incluido el hallazgo de que `SETFILEPATH` no
  refresca un `Note` ya asignado — ver [§3.2](#32--crear-y-actualizar-el-note-con-resourcetool-verificado-en-vivo)
- Chris Zukowski — howtomarketagame.com — <https://howtomarketagame.com/> · 200 OK hoy (raíz
  reverificada); la cita concreta sobre «decidir el género y mantenerse en él» ya está verificada
  y enlazada en [13 · 11 §6.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#61-la-página-de-steam-es-el-primer-hito-de-marketing-no-el-último),
  y este documento la reutiliza sin volver a citarla entera

**Marcado con ⚠️ en el texto.** Las secciones de monetización (2.16) y de meta-progresión dentro
de progresión (2.8), que la auditoría `_indice/auditorias/diseno-gdd.md` (I3-I6, D3-D4) señalaba
como huecos de esta biblioteca, se cerraron un día después con
[13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md) y
[13 · 16](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md)
(verificado por la auditoría `_indice/auditorias/r4-combate-colisiones-gdd.md`, 7-sep-2026); ya no
hacen falta plantillas inventadas para ninguna de las dos. La distinción entre pitch de venta y
pitch de diseño en §1.4 es
síntesis propia a partir de Fullerton y de la práctica del oficio, no una cita literal de un
artículo que trace esa línea con esas palabras. El diagrama de economía con notación formal
(Machinations) queda fuera de alcance y se marca así en §2.20, en vez de improvisar una notación.
