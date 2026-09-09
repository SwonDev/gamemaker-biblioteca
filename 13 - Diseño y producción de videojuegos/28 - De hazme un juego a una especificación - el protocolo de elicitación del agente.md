# 28 · De «hazme un juego» a una especificación — el protocolo de elicitación del agente

> Qué preguntar cuando el encargo es una sola frase, cuántas veces preguntar, y qué asumir si el
> usuario contesta «lo que veas» — que es el caso más frecuente. Esto pasa **antes** de que exista
> ningún documento de diseño:
> [13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla)
> y [13 · 14 §2](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso)
> ya dan la plantilla de qué se escribe una vez que hay respuestas; este documento da el método
> para conseguir esas respuestas sin inventarlas y sin interrogar al usuario veinte minutos.
>
> **Qué NO cubre.** Cómo se ve una especificación completa, lista para que un agente la
> implemente sin adivinar —reglas numeradas, rangos, recorte explícito, criterio de aceptación—
> ya está resuelto en
> [13 · 14 §6](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#6--la-versión-para-llm-qué-necesita-un-agente-para-implementar-sin-inventar),
> con el ejemplo completo «Luz de Ámbar» en
> [§6.3](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#63--ejemplo-real-un-plataformas-de-3-niveles):
> no se repite aquí, se usa tal cual en los bloques 1-2 de la plantilla de [§3.1](#31--la-plantilla-de-especificación-mínima).
> Cómo se ordenan los sistemas ya fichados y se convierten en recursos concretos de GameMaker está
> en [13 · 14 §7](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#7--del-gdd-al-proyecto-la-lista-de-tareas-y-el-árbol-de-recursos).
> El calendario de fases de un proyecto que sí va a durar semanas o meses —prototipo, vertical
> slice, alfa, beta— sigue en
> [13 · 11 §2](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#2--fases-y-hitos-las-puertas-del-proyecto),
> pensado para ese calendario humano; si tu especificación resulta ser la de una sola sesión de
> agente, el criterio de cierre correcto es el bloque 4 de la plantilla de
> [§3.1](#31--la-plantilla-de-especificación-mínima), no esas fases.

---

## 1 · Los principios

### 1.1 · A quién le hace falta esto

Todo lo demás en `13 - Diseño y producción de videojuegos/` da por hecho que alguien ya rellenó
los campos de un documento de diseño —pitch, público, plataforma, recorte— **antes** de que
empiece la sección que un agente lee. Este documento cubre la capa que falta: la conversación de
un turno que convierte «hazme un juego de plataformas» en esos campos rellenos.

Hace falta exactamente cuando el encargo llega como una frase suelta y no como un documento ya
escrito. Si el usuario ya trae un GDD, una ficha de sistema, o ya contestó dentro de su propia
petición a la mayoría de las preguntas de [§2.1](#21--las-preguntas-de-arranque) («un
metroidvania de dos horas, en PC, sin historia, como Hollow Knight pero sin combate»), no hay
interrogatorio que hacer: se aplica [§1.3](#13--no-preguntes-lo-que-ya-te-han-dicho) y se pasa
directo a escribir. Este documento no es un trámite obligatorio de siete preguntas; es un método
para no adivinar lo que nadie te ha dicho.

### 1.2 · Preguntar ahora es barato; adivinar y corregir después no lo es

La razón de fondo por la que esta capa importa no es de estilo, es de coste. Barry Boehm
documentó, con datos reales de proyectos en TRW e IBM durante los 70, que **el coste de corregir
un error crece según la fase del proyecto en la que se detecta**: de una hora de análisis si se
encuentra mientras se recogen los requisitos, a un orden de magnitud mayor si se encuentra en
diseño o código, y mucho más si el proyecto ya está en producción (*Software Engineering
Economics*, Prentice-Hall, 1981; el hallazgo original usa rangos —de 3-8× en diseño a 50-200× en
producción según el proyecto—, no la cifra redonda «1-10-100» que popularizó después el sector,
que simplifica de más). El caso de un agente de IA construyendo un juego es el mismo problema con
la fase de «requisitos» comprimida a un único turno de chat: **una pregunta antes de escribir la
primera línea cuesta una respuesta; la misma ambigüedad descubierta después de fichar tres
sistemas, escribir el `.gml` y compilarlos cuesta rehacerlos.** El resto de este documento existe
para que esa pregunta se haga en el momento barato.

### 1.3 · No preguntes lo que ya te han dicho

Un agente disciplinado que aplicara [§2.1](#21--las-preguntas-de-arranque) al pie de la letra,
sin este principio, le preguntaría el género a alguien que ya escribió «un roguelike de mazmorras
con permadeath, para PC, sin historia». Antes de preguntar nada:

1. Relee la petición del usuario completa, buscando respuesta a cada una de las preguntas de
   [§2.1](#21--las-preguntas-de-arranque).
2. Marca como **ya respondida** cualquier pregunta cuya respuesta ya esté en la frase, aunque sea
   implícita («como Vampire Survivors» ya contesta género y referencia; «para jugar en el móvil
   de camino al trabajo» ya contesta plataforma y duración de partida).
3. Pregunta **solo** lo que de verdad falta, en el único turno de [§2.2](#22--el-criterio-de-parada).

### 1.4 · Una sola pasada, no un interrogatorio

Un humano que aceptara un encargo de diseño no le hace ocho preguntas una detrás de otra,
esperando respuesta a cada una antes de la siguiente: las agrupa en una sola conversación. Un
agente hace lo mismo — **todas las preguntas que falten, en un único bloque, en el mismo turno**,
nunca una detrás de otra a la espera de que el usuario conteste antes de mostrar la siguiente. La
biblioteca es deliberadamente agnóstica de qué CLI o herramienta de interfaz usa cada agente para
esto (formulario de opción múltiple, texto libre, lo que ofrezca la sesión): lo que importa no es
el mecanismo, es que sea **una sola pasada**. El criterio de cuándo repreguntar, que es la única
excepción admitida, está en [§2.2](#22--el-criterio-de-parada).

### 1.5 · Decidido por el usuario frente a asumido por defecto — y por qué se distinguen

Cada respuesta a las preguntas de [§2.1](#21--las-preguntas-de-arranque) tiene dos procedencias
posibles: el usuario la dio, o el agente aplicó el valor por defecto de [§2.3](#23--los-valores-por-defecto)
porque no hubo respuesta. Un documento de diseño que no distingue las dos cosas no es auditable:
si dentro de tres sistemas el usuario dice «yo nunca pedí que hubiera historia», no hay forma de
saber, leyendo la especificación, si fue una petición explícita, un default razonable, o un
malentendido. La plantilla de [§3.1](#31--la-plantilla-de-especificación-mínima) por eso marca
cada respuesta del bloque 0 con `[USUARIO]` o `[DEFAULT]` — una palabra, no una nota al margen —
y esa marca se arrastra a cualquier campo de un GDD completo ([13 · 14 §2](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso))
que ese bloque 0 alimente.

### 1.6 · Lo que no está decidido se señala como pregunta abierta, nunca se implementa por iniciativa propia

Esta es la regla que gobierna todo lo demás en este documento, y por eso va aquí de primer nivel
en vez de vivir escondida dentro de un ejemplo. Cuando una regla es ambigua, un parámetro no tiene
rango, o el usuario pide algo que el recorte explícito de la especificación ya excluyó, **el
agente lo dice y espera respuesta — no rellena el hueco con la opción que le parece razonable.**
Es la misma condición que ahora es la quinta de
[13 · 14 §6.1](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#61--qué-hace-que-un-gdd-sea-implementable-y-no-solo-leíble)
(«qué hace que un GDD sea implementable»); aquí se repite como principio, no como cita, porque
aplica en dos momentos distintos que ese documento no cubre: **durante la elicitación misma**
(§1.3-1.5 de aquí, cuando una respuesta a [§2.1](#21--las-preguntas-de-arranque) sigue siendo
ambigua tras la única repregunta de [§2.2](#22--el-criterio-de-parada)) y **durante un cambio de
idea a mitad de la construcción** ([§2.4](#24--cuando-el-usuario-cambia-de-idea-a-mitad-el-umbral)).
En ambos casos el mecanismo es el mismo: se escribe la pregunta abierta en el documento —en el
bloque 0 si es de arranque, en el bloque 5 si es de un cambio a mitad— y no se avanza ese punto
concreto hasta tener respuesta. El resto de la especificación sigue construyéndose con
normalidad: una pregunta abierta bloquea el campo que afecta, no el proyecto entero.

---

## 2 · El método, paso a paso

### 2.1 · Las preguntas de arranque

Ocho preguntas, ni una más. Cada una alimenta un campo concreto de un documento ya existente en
esta biblioteca — ninguna se inventa sin destino. Fórmulas reales, no casillas de plantilla: así
es como se le preguntan a una persona.

| # | Pregunta | Por qué esta y no otra | A qué campo alimenta |
|---|---|---|---|
| 1 | **Género y referencia.** «¿A qué se parece? Descríbemelo como "X se encuentra con Y", o dime un juego que ya conozcas.» | Es la decisión de la que dependen todas las demás: el género fija qué sistemas hacen falta antes de que exista ninguno | Pitch y Referencias de [13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla); Concepto y pitch de [13 · 14 §2.2](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso) |
| 2 | **Alcance de esta sesión.** «¿Quieres algo jugable hoy mismo, o construimos un proyecto más grande en varias sesiones?» | Decide si el criterio de cierre es el bloque 4 de este documento o las fases de semanas/meses de [13 · 11 §2](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#2--fases-y-hitos-las-puertas-del-proyecto) | RECORTE de [13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla) |
| 3 | **Plataforma y control de destino.** «¿Dónde se juega: PC con teclado, con mando, o móvil táctil?» | Cambia el diseño del sistema 1 (input), no un ajuste posterior — la tabla completa de consecuencias por plataforma ya existe y no se repite aquí | [13 · 14 §2.5](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#25--público-plataformas-y-competencia-el-método) |
| 4 | **Arte.** «¿Aportas tú los sprites y sonidos, o los genero yo?» | Decide si el primer sistema usa placeholders generados por código desde el minuto uno o espera assets del usuario — no es una pregunta de estilo, es de secuencia de trabajo | Escalera de placeholders de [12 · 09 §5](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#5--assets-sin-artista) y [13 · 09 §8 bis](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad) |
| 5 | **Historia.** «¿Lleva narrativa, o es un arcade sin historia?» | Un sistema entero (biblia del mundo, fichas de personaje, diálogo) que no se construye si la respuesta es «no» | Personajes, mundo y narrativa de [13 · 14 §2.11](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso) |
| 6 | **Jugadores.** «¿Un jugador, o multijugador local u online?» | Cambia la arquitectura desde el sistema 1 (input, cámara, guardado) — decidirlo después de programar el sistema 1 en solitario significa rehacerlo | Verbos y arquitectura técnica de [13 · 14 §2.6](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso) y §2.15; implementación en `04 - Recetas por género/` |
| 7 | **Duración objetivo de partida.** «¿Cuánto dura una partida, o una sesión de juego típica?» | Fija el bucle de sesión antes de diseñar el de acción, no al revés | Casilla «Plataforma · duración de partida · público» de [13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla); bucle de sesión de [13 · 01 §2.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#21--los-tres-relojes) |
| 8 | **Para qué es.** «¿Es para probar una idea o aprender, para publicarlo gratis, o para venderlo?» | Decide si arrastra toda la maquinaria de producción de [13 · 11](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) y de modelo de negocio de [13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md), o si el agente puede saltárselas por completo | [13 · 11 §1.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#11-el-principio); modelo de negocio en [13 · 20 §2.1](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md#21--elegir-el-modelo-antes-de-diseñar-ningún-sistema) |

> 💡 **Por qué estas ocho y no más.** Un artículo del oficio sobre briefs de encargo a estudios
> externos (Twine, *How to Write a Project Brief for a Game Developer*, ver [Fuentes](#fuentes))
> reduce lo imprescindible a género y mecánicas, público y plataforma, y estilo visual — el mismo
> núcleo que las preguntas 1, 3 y 4 de arriba, ampliado aquí con lo que ese caso (un estudio
> encargando a otro estudio, con semanas de por medio) no necesita resolver de entrada y una
> sesión de agente sí: alcance de la sesión, historia sí/no, jugadores y para qué es. No hay una
> novena pregunta candidata que alimente un campo que estas ocho no cubran ya — si aparece un
> proyecto que de verdad la necesite, es una señal de que ese proyecto ya no es «hazme un juego»
> desde cero, sino un encargo con su propio brief, y este documento no es el que lo cubre.

### 2.2 · El criterio de parada

Un agente no puede interrogar veinte minutos. La regla es corta:

1. **Todo en un único bloque, nunca secuencial.** Las preguntas que falten ([§1.3](#13--no-preguntes-lo-que-ya-te-han-dicho))
   se hacen todas a la vez, en el mismo turno.
2. **Como máximo, una repregunta — y solo sobre dos de las ocho.** Si tras la primera ronda la
   respuesta a la pregunta 2 (alcance) o a la 3 (plataforma) sigue siendo ambigua, esas dos
   justifican una segunda vuelta corta y **solo esas dos**: son las que más cambian el sistema 1
   ([13 · 14 §2.5](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#25--público-plataformas-y-competencia-el-método)
   documenta hasta qué punto la plataforma cambia el diseño del input desde el primer prototipo).
   El resto de las ocho, si sigue sin respuesta después de la primera ronda, toma directamente el
   valor por defecto de [§2.3](#23--los-valores-por-defecto): no hay una tercera pregunta sobre
   ellas.
3. **Nunca una segunda ronda sobre la misma pregunta dos veces.** Si tras la repregunta del punto
   2 la respuesta sigue sin llegar o sigue siendo ambigua, se aplica igualmente el valor por
   defecto y se marca `[DEFAULT — respuesta ambigua tras repregunta]` en el bloque 0 de la
   especificación, en vez de seguir preguntando.
4. **Escribir y enseñar, no seguir hablando.** En cuanto hay una respuesta —dada por el usuario o
   por defecto— para las ocho preguntas, el siguiente paso es escribir la especificación de
   [§3.1](#31--la-plantilla-de-especificación-mínima) y enseñarla, no seguir conversando sobre
   ella.

### 2.2 bis · Cuando no hay a quién preguntar: el encargo cerrado

Todo lo anterior supone una conversación. **Cada vez más, no la hay**: un agente lanzado como
tarea de fondo, desde un *issue*, desde un *cron* o desde otro agente recibe un encargo de un
solo sentido y **no tiene canal de vuelta**. Ahí la regla «pregunta todo en un turno y enseña la
especificación antes de crear el proyecto» no es que se incumpla: es que **no tiene forma**. No
hay a quién preguntar ni a quién enseñar.

Este apartado existe porque pasó de verdad: un agente construyó un juego completo siguiendo esta
biblioteca, se saltó el paso 0 por este motivo exacto, y lo dejó anotado en vez de disimularlo
([`r12-prueba-plataformas.md` §7](../_indice/auditorias/r12-prueba-plataformas.md)).

**Qué hacer cuando no hay canal:**

1. **No preguntes al vacío.** Un turno de preguntas que nadie va a leer solo retrasa el trabajo.
2. **Aplica los valores por defecto de [§2.3](#23--los-valores-por-defecto) a todas las preguntas
   sin respuesta**, exactamente igual que si el usuario no hubiera contestado a esa parte.
3. **Escribe la especificación igual.** El documento no es un trámite para el usuario: es lo que
   te impide improvisar el alcance a mitad de camino. Sin él, en el minuto cuarenta ya no
   recuerdas qué decidiste y qué inventaste.
4. **Marca cada valor asumido con `[DEFAULT]`**, con el mismo rigor de
   [§1.5](#15--decidido-por-el-usuario-frente-a-asumido-por-defecto--y-por-qué-se-distinguen).
   Aquí importa **más** que en una conversación, no menos: es lo único que le dirá a quien
   recoja el trabajo qué decidió él y qué decidiste tú por él.
5. **Entrégala CON el juego, no antes.** Es el único cambio de orden que autoriza este documento,
   y solo aquí. La especificación pasa de ser una puerta a ser parte del entregable: va junto al
   proyecto, y en el mensaje final se dice qué se asumió y qué habría cambiado el resultado.
6. **Di explícitamente que no hubo canal.** «Asumí X, Y y Z porque el encargo no lo decía y no
   había forma de preguntar» es una frase que el usuario necesita leer. El silencio convierte
   una suposición razonable en un error tuyo.

### El tercer caso: hay canal, pero te han vetado planificar

Entre «puedo preguntar» y «no puedo preguntar» hay un tercer supuesto, y es más frecuente de lo
que parece: **el usuario está ahí y te ha dicho explícitamente que no quiere un plan** — «no me
preguntes, hazlo», «nada de planificar, al lío», «no quiero un documento, quiero el juego». Un
agente que aplique el caso anterior aquí se estará escudando en él para saltarse el paso 0; y uno
que insista en preguntar estará desobedeciendo una instrucción clara.

La salida no es ninguna de las dos:

1. **No preguntes, y no lo discutas.** Te han dado una instrucción sobre el método, no sobre el
   alcance. Se respeta.
2. **Escribe la especificación igual, y no la enseñes.** Deja de ser una puerta y pasa a ser tu
   propia herramienta: es lo que te impide improvisar el alcance en el minuto cuarenta. Escribirla
   cuesta dos minutos y no gasta ni un turno del usuario.
3. **Entrégala con el juego**, como en el caso anterior, marcando lo asumido con `[DEFAULT]`.
4. **En el mensaje final, tres líneas**: qué asumiste, y cuál de esas suposiciones cambiaría más
   el resultado si te equivocaste. No es planificar: es decir de qué pie cojea lo que entregas.

Lo que **no** vale es tomar el veto a planificar como permiso para no decidir. Las ocho preguntas
siguen teniendo respuesta —la des tú o la dé el valor por defecto—; lo único que cambia es que no
se la preguntas a nadie.

> ⚠️ **No lo uses como atajo.** Si tienes canal —una conversación, un turno de vuelta, cualquier
> forma de que la respuesta te llegue— y **nadie te ha vetado preguntar**, **pregunta**. Este apartado es para cuando el canal no
> existe, no para cuando preguntar da pereza o parece que ralentiza. Confundir las dos cosas es
> volver a «hazme un juego» → programar sin especificación, que es justo lo que este documento
> existe para evitar.

### 2.3 · Los valores por defecto

Para cuando el usuario contesta «lo que veas», «sorpréndeme», o simplemente no responde a una
pregunta concreta. Cada default está anclado a una regla que ya existe en la biblioteca — ninguno
es un «depende» disfrazado.

| # | Pregunta | Valor por defecto | Por qué este y no otro |
|---|---|---|---|
| 1 | Género y referencia | Arcade sencillo de recorrido corto — un plataformas de pocas pantallas, sin verbos que inventar. Referencia interna concreta: el propio ejemplo de [13 · 14 §6.3](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#63--ejemplo-real-un-plataformas-de-3-niveles), «Luz de Ámbar», ya verificado símbolo por símbolo | [13 · 11 §1.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#11-el-principio): «tu primer juego terminado tiene que ser pequeño» |
| 2 | Alcance de esta sesión | El mínimo defendible: algo jugable y que compile hoy, nunca el máximo imaginable | [13 · 11 §1.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#11-el-principio) |
| 3 | Plataforma y control | PC, teclado — la fila que no exige decisiones extra de zonas seguras táctiles ni de navegación con mando desde el primer prototipo | [13 · 14 §2.5](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#25--público-plataformas-y-competencia-el-método), fila PC |
| 4 | Arte | Lo genera el agente: primitivas de dibujo o un PNG plano generado por código, con nombre definitivo desde el primer momento; audio sintetizado en runtime | [12 · 09 §5](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#5--assets-sin-artista) y [13 · 09 §8 bis](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad) |
| 5 | Historia | No. Arcade puro; si se escribe un GDD completo, la sección 2.11 de [13 · 14](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso) se marca «No aplica: sin narrativa por defecto», nunca se deja vacía sin explicación | Checklist de [13 · 14 §4](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#4--checklist): «una sección vacía sin explicación es indistinguible de un olvido» |
| 6 | Jugadores | Un jugador | Es la opción que no obliga a decidir sincronización, sesiones o *matchmaking* antes de que exista ningún sistema — la implementación de multijugador, si hace falta después, está resuelta aparte en `04 - Recetas por género/` |
| 7 | Duración objetivo de partida | Sesión corta: unos minutos, no una partida de una hora | Coherente con el default 2 (alcance mínimo) |
| 8 | Para qué es | Para probar o aprender. No arrastra la maquinaria de [13 · 11](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) (fases, lanzamiento) ni de [13 · 20](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md) (modelo de negocio) salvo que el usuario lo pida explícitamente después | [13 · 11 §1.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#11-el-principio) y [13 · 20 §2.1](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md#21--elegir-el-modelo-antes-de-diseñar-ningún-sistema) |

Cada default aplicado se escribe en el bloque 0 de la especificación con la marca `[DEFAULT]`
junto a la respuesta ([§1.5](#15--decidido-por-el-usuario-frente-a-asumido-por-defecto--y-por-qué-se-distinguen)).
No es una nota interna del agente: es parte del documento que el usuario lee, precisamente para
que pueda corregir cualquier default con el que no esté de acuerdo con una frase, no reescribiendo
el proyecto entero.

### 2.4 · Cuando el usuario cambia de idea a mitad: el umbral

A media construcción, «en realidad que no tenga jefe final» o «añádele un multijugador local» no
se resuelven igual. El criterio reutiliza la misma matriz que ya decide qué se recorta en
[13 · 11 §1.5](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#15-la-matriz-de-recorte)
(«toca el core loop» — el minuto a minuto cambia si se quita — frente a lo que no lo toca),
aplicada a un cambio que llega en vivo en vez de a una decisión de recortar:

| El cambio pedido… | Es… | Qué hace el agente |
|---|---|---|
| **No toca el core loop** y no invalida ningún sistema ya marcado «implementado» en la especificación (estado de [13 · 01 §8.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#82--ficha-por-sistema--plantilla)) | Un **ajuste menor** | Se aplica. Se anota un ADR ligero de una línea ([13 · 11 §3.5](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#35-registro-de-decisiones-adr-ligero)) en el bloque 5 de la especificación y se sigue construyendo sin más trámite |
| **Sí toca el core loop**, o invalida un sistema ya marcado «implementado» | Un **cambio de proyecto** | El agente **para** — no parchea en silencio — y pregunta explícitamente si reescribir la especificación desde el bloque 0 (o desde el campo concreto afectado) hacia abajo. No sigue construyendo sobre la especificación vieja mientras esa pregunta esté abierta — es la misma regla de [§1.6](#16--lo-que-no-está-decidido-se-señala-como-pregunta-abierta-nunca-se-implementa-por-iniciativa-propia) |

**Qué hacer con lo ya construido que un cambio de proyecto invalida.** No se descarta por
iniciativa propia. El agente escribe, en la misma pregunta abierta del bloque 5, qué sistemas
quedan obsoletos con el cambio propuesto y espera la decisión del usuario: seguir usándolos tal
cual, adaptarlos, o descartarlos. Descartar trabajo ya hecho sin que el usuario lo haya decidido
es exactamente el tipo de invención que [§1.6](#16--lo-que-no-está-decidido-se-señala-como-pregunta-abierta-nunca-se-implementa-por-iniciativa-propia)
prohíbe, aplicada al sentido contrario: tan inventado es añadir algo que nadie pidió como borrar
algo que nadie pidió borrar.

El mecanismo de feature creep de
[13 · 11 §1.6](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#16-feature-creep-y-cómo-se-frena)
(lista congelada, cuaderno de ideas, «¿esto acerca o aleja la fecha?») sigue aplicando tal cual
cuando la especificación de este documento resulta ser la de un proyecto largo; para la sesión
corta de un agente, la pregunta equivalente es más simple todavía: **¿este cambio cabe en la
sesión que ya se acordó en la pregunta 2, o la sesión que se acordó ya no describe lo que se está
construyendo?** Si la respuesta es la segunda, es un cambio de proyecto aunque técnicamente no
toque el core loop.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 · La plantilla de especificación mínima

Extiende el GDD de una página de
[13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla)
—que no se toca ni se duplica— con los bloques que le faltan para ser el punto de partida
completo de una sesión de agente: de dónde salieron las respuestas, en qué orden se construye, y
qué pasa si el usuario cambia de idea.

```markdown
# <Título> · Especificación de sesión          versión: 0.1 · fecha: AAAA-MM-DD

## 0 · Preguntas y respuestas
(las ocho preguntas de §2.1, con la respuesta real del usuario marcada [USUARIO] o el
 valor por defecto de §2.3 marcado [DEFAULT] — trazabilidad exigida por §1.5)
1. Género y referencia:
2. Alcance de esta sesión:
3. Plataforma y control:
4. Arte (aporta el usuario / lo genera el agente):
5. Historia (sí/no, cuánta):
6. Jugadores (uno / local / online):
7. Duración objetivo de partida:
8. Para qué es (probar/aprender · publicar gratis · vender):

## 1 · GDD de una página
(la plantilla completa de 13/01 §8.1, sin repetirla aquí — pitch, MDA, verbos, bucles,
 recorte, riesgo, métrica de éxito; cada campo alimentado por las respuestas del bloque 0)

## 2 · Sistemas
(una ficha por sistema, en la versión para LLM de 13/14 §6.2 — reglas numeradas, rango,
 símbolos GML probables, fuera de alcance — mínimo el sistema que sostiene el pilar
 principal; el ejemplo completo de 13/14 §6.3 muestra cómo se ve terminada)

## 3 · Orden de construcción
(aplica la tabla de categorías de 13/14 §7.2 a los sistemas fichados en el bloque 2;
 si aparece un ciclo de dependencia al cruzarlos, para y dilo — no lo resuelvas adivinando)

## 4 · Checklist de cierre
(el criterio de aceptación de "Cómo se prueba" de cada ficha del bloque 2 — la tarea no
 está terminada hasta que cada casilla se cumple Y `gm-cli compile` sale limpio)

## 5 · Qué hacer si el usuario cambia de idea
(vacío hasta que ocurra; cuando ocurra, aplica el umbral de §2.4 — ajuste menor: una
 línea de ADR aquí mismo y seguir; cambio de proyecto: la pregunta abierta que bloquea
 el campo afectado, con los sistemas que quedan obsoletos y a la espera de respuesta)
```

Nada de esto sustituye la verificación de símbolos GML que exige `AGENTS.md §1`
(`python3 "_indice/buscar.py" <símbolo>` antes de escribir cualquier función): la especificación
resuelve la ambigüedad de **qué** construir, no libra de comprobar que la función existe.

### 3.2 · Ejemplo: de una frase a la especificación

Petición del usuario, completa: *«Hazme un juego de plataformas, algo cortito, lo que veas.»*

Aplicando [§1.3](#13--no-preguntes-lo-que-ya-te-han-dicho): la pregunta 1 (género) ya está
contestada — «plataformas» — y la 2 (alcance) tiene una pista fuerte —«algo cortito»— aunque no
un número. Quedan sin contestar 3, 4, 5, 6, 7 y 8. En un único turno ([§2.2](#22--el-criterio-de-parada))
se preguntan esas seis; el usuario responde solo a la de plataforma («en el ordenador») y deja el
resto en silencio. Con el criterio de parada, eso no es motivo de una segunda ronda —plataforma ya
quedó resuelta y ninguna otra pregunta pendiente entra en la excepción de repregunta— así que el
resto toma el valor por defecto de [§2.3](#23--los-valores-por-defecto):

```markdown
## 0 · Preguntas y respuestas
1. Género y referencia: plataformas [USUARIO]
2. Alcance de esta sesión: algo jugable hoy, corto [USUARIO — «cortito» interpretado como
   el mínimo defendible del default 2, sin número exacto dado]
3. Plataforma y control: PC, teclado [USUARIO]
4. Arte: lo genera el agente, primitivas y PNG por código [DEFAULT]
5. Historia: no, arcade puro [DEFAULT]
6. Jugadores: uno [DEFAULT]
7. Duración objetivo de partida: sesión corta, unos minutos [DEFAULT]
8. Para qué es: para probar/aprender [DEFAULT]
```

Con las ocho preguntas resueltas —tres por el usuario, cinco por defecto, todas marcadas—, el
bloque 1 se rellena con la plantilla de
[13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla)
y el bloque 2 con fichas de sistema en la forma de
[13 · 14 §6.2](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#62--la-plantilla-mínima-para-llm):
el resultado, para un plataformas corto de un jugador sin historia en PC, es exactamente la forma
—y podría ser el contenido— del ejemplo ya verificado de
[13 · 14 §6.3](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#63--ejemplo-real-un-plataformas-de-3-niveles),
«Luz de Ámbar»: no es casualidad, es el mismo default 1 de [§2.3](#23--los-valores-por-defecto)
señalándolo como la referencia interna concreta para este caso, el más común de todos.

### 3.3 · Dónde vive la especificación antes de que exista el proyecto

Antes de `gm-cli init`, la especificación es un archivo de trabajo en la conversación o en el
sistema de archivos del agente — todavía no hay `.yyp` en el que crear un recurso `Notes`. En
cuanto el proyecto existe, se traslada al recurso `Notes` del propio proyecto exactamente con el
método ya verificado en
[13 · 14 §3.1-3.2](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#31--guardar-el-gdd-como-recurso-notes-del-proyecto)
(`resource create type=notes`, `NOTE SETFILEPATH`, y el hallazgo de que hay que borrar y
recrear el recurso para refrescarlo — no se repite aquí). El bloque 5 («qué hacer si el usuario
cambia de idea») se actualiza en el mismo `Note`, con el mismo mecanismo, cada vez que ocurre un
cambio: es el ADR ligero de [§2.4](#24--cuando-el-usuario-cambia-de-idea-a-mitad-el-umbral) escrito
en el sitio donde ya vive el resto de la especificación, no en un archivo aparte.

---

## 4 · Checklist

**Antes de escribir la primera pregunta**

- [ ] Se releyó la petición completa del usuario y se marcó qué preguntas de
      [§2.1](#21--las-preguntas-de-arranque) ya están contestadas ([§1.3](#13--no-preguntes-lo-que-ya-te-han-dicho))
- [ ] Lo que falta se va a preguntar en un único bloque, no una pregunta detrás de otra

**Antes de escribir la especificación**

- [ ] Las ocho preguntas tienen respuesta, cada una marcada `[USUARIO]` o `[DEFAULT]`
- [ ] Ninguna pregunta se repreguntó más de una vez, y solo alcance o plataforma llegaron a
      repreguntarse
- [ ] Ningún default se aplicó sin su ancla de [§2.3](#23--los-valores-por-defecto): si hiciera
      falta un default nuevo que esta tabla no cubre, se escribe con criterio propio y se marca
      ⚠️, no se inventa una regla que suene a esta biblioteca sin serlo

**Antes de crear el proyecto**

- [ ] La especificación completa (bloques 0-5 de [§3.1](#31--la-plantilla-de-especificación-mínima))
      está escrita y se le ha **enseñado al usuario**, no solo redactado para uso interno del
      agente
- [ ] No se ha ejecutado `gm-cli init` ni ninguna otra herramienta de creación de proyecto antes
      de este punto

**Durante la construcción, si el usuario pide un cambio**

- [ ] Se aplicó el umbral de [§2.4](#24--cuando-el-usuario-cambia-de-idea-a-mitad-el-umbral) antes
      de tocar código: ajuste menor → ADR de una línea y seguir; cambio de proyecto → parar y
      preguntar
- [ ] Si el cambio invalida trabajo ya hecho, se ha dicho explícitamente qué sistemas quedan
      obsoletos, sin descartar nada por iniciativa propia

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo se evita |
|---|---|---|
| **Crear el proyecto con `gm-cli init` antes de escribir la especificación** | «Hazme un juego de plataformas» ya parece un encargo completo, así que se salta la elicitación | El paso 0 de `SKILL.md` y de `AGENTS.md §5`: sin especificación escrita y enseñada, no hay paso siguiente |
| **Preguntar las ocho, aunque la mitad ya estén contestadas** | Aplicar la lista de [§2.1](#21--las-preguntas-de-arranque) al pie de la letra, sin pasar primero por [§1.3](#13--no-preguntes-lo-que-ya-te-han-dicho) | Releer la petición completa antes de preguntar nada; marcar lo ya contestado |
| **Preguntar una a una, esperando respuesta antes de la siguiente** | Cada pregunta parece más clara aislada | El criterio de parada de [§2.2](#22--el-criterio-de-parada): todas en el mismo turno |
| **Repreguntar sobre las seis preguntas que no son alcance ni plataforma** | Parece más cuidadoso insistir hasta tener una respuesta explícita a todo | Solo alcance y plataforma admiten una repregunta; el resto toma el default de [§2.3](#23--los-valores-por-defecto) y sigue |
| **Aplicar un default sin marcarlo** | Es más rápido escribir el valor directamente que anotar `[DEFAULT]` | La marca es lo que hace la especificación auditable ([§1.5](#15--decidido-por-el-usuario-frente-a-asumido-por-defecto--y-por-qué-se-distinguen)); sin ella, un desacuerdo posterior del usuario no se puede rastrear a su origen |
| **Tratar cualquier petición nueva a mitad de sesión como un ajuste menor** | Parece más productivo seguir construyendo sin interrumpir | Aplicar la matriz de [§2.4](#24--cuando-el-usuario-cambia-de-idea-a-mitad-el-umbral): si toca el core loop o invalida un sistema «implementado», es un cambio de proyecto, no un matiz |
| **Rellenar una ambigüedad con la opción que "suena razonable"** | El agente no pregunta por defecto: inventa una respuesta plausible en vez de decir que no sabe | La regla de [§1.6](#16--lo-que-no-está-decidido-se-señala-como-pregunta-abierta-nunca-se-implementa-por-iniciativa-propia): se señala como pregunta abierta, nunca se implementa por iniciativa propia |
| **Descartar sistemas ya construidos porque el nuevo pedido "ya no los necesita"** | Parece limpieza razonable | Se pregunta primero ([§2.4](#24--cuando-el-usuario-cambia-de-idea-a-mitad-el-umbral)): descartar sin que lo decida el usuario es la misma invención que añadir algo que nadie pidió |
| **Aplicar literalmente las fases de semanas de `13/11 §2` a una sesión de una tarde** | El documento de producción es correcto y está a mano, así que se usa tal cual | Si la pregunta 2 de [§2.1](#21--las-preguntas-de-arranque) dio como respuesta «esta sesión», el criterio de cierre es el bloque 4 de [§3.1](#31--la-plantilla-de-especificación-mínima), no las puertas de fase de [13 · 11 §2](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#2--fases-y-hitos-las-puertas-del-proyecto) |

---

## Ver también

- [13 · 01 §8](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#8--el-documento-de-diseño-ligero) — el GDD de una página y la ficha por sistema que el bloque 1-2 de la plantilla de este documento rellena, sin repetir
- [13 · 14 §1.1](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#11--cuándo-el-one-pager-no-basta) — cuándo el one-pager de arriba no basta y hace falta el GDD completo, incluida la señal 4 («un LLM va a implementar veinte sistemas»), que es justo el caso de uso de este documento
- [13 · 14 §6](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#6--la-versión-para-llm-qué-necesita-un-agente-para-implementar-sin-inventar) — la versión de una ficha de sistema que un agente puede implementar sin inventar, con el ejemplo completo de §6.3 que reutiliza este documento en §3.2
- [13 · 14 §7](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#7--del-gdd-al-proyecto-la-lista-de-tareas-y-el-árbol-de-recursos) — el orden entre sistemas y el paso de una ficha a los recursos concretos de GameMaker, que rellena el bloque 3 de la plantilla de §3.1
- [13 · 11 §1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#1--alcance-el-único-problema-que-de-verdad-mata-juegos) — el alcance mínimo defendible (§1.1), la matriz de recorte (§1.5) y el feature creep (§1.6) que fundamentan los defaults de §2.3 y el umbral de §2.4
- [13 · 11 §2](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#2--fases-y-hitos-las-puertas-del-proyecto) — las fases de un proyecto que sí dura semanas o meses, para cuando la pregunta 2 de §2.1 responde eso
- [13 · 11 §3.5](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#35-registro-de-decisiones-adr-ligero) — el ADR ligero que anota un ajuste menor en el bloque 5 de la especificación
- [13 · 20 §2.1](./20%20-%20Modelo%20de%20negocio,%20monetización%20y%20ética%20del%20diseño.md#21--elegir-el-modelo-antes-de-diseñar-ningún-sistema) — el árbol de decisión de modelo de negocio que solo se recorre si la pregunta 8 de §2.1 responde «vender» o «publicar»
- [12 · 09 §5](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#5--assets-sin-artista) y [13 · 09 §8 bis](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad) — la escalera de placeholders que aplica el default de la pregunta 4
- [SKILL.md](../_indice/skills/gamemaker-biblioteca/SKILL.md) y [AGENTS.md](../AGENTS.md) — los puntos de entrada que exigen escribir y enseñar esta especificación antes de crear el proyecto
- [_indice/auditorias/r5-spec-driven.md](../_indice/auditorias/r5-spec-driven.md) — la auditoría que encarga este documento y verifica, leyendo los tres puntos de entrada, que ninguno obligaba a esto antes de existir este documento

---

## Fuentes

Consultadas y verificadas en vivo el **2026-09-08**.

- Barry Boehm — *Software Engineering Economics*, Prentice-Hall, 1981 (el hallazgo original se
  presentó antes en *Software Engineering*, IEEE Transactions on Computers, 1976) — el coste de
  corregir un requisito crece según la fase en la que se detecta, con rangos de 3-8× en diseño a
  50-200× en producción según el proyecto; verificado a través de una síntesis secundaria
  ([reworkcost.com/boehm-cost-of-change-curve](https://reworkcost.com/boehm-cost-of-change-curve),
  200&nbsp;OK hoy) que además señala que la cifra redonda «1-10-100» es una popularización
  posterior del sector, no el dato original — se cita aquí con esa matización explícita en vez de
  la cifra simplificada, siguiendo la misma disciplina de esta biblioteca de no repetir un número
  bonito sin comprobarlo
- Twine — *How to Write a Project Brief for a Game Developer* —
  <https://www.twine.net/blog/how-to-write-a-project-brief-for-a-game-developer/> · 200&nbsp;OK
  hoy · el núcleo mínimo de un brief de encargo a un estudio (género y mecánicas, público y
  plataforma, estilo visual) que fundamenta la nota de [§2.1](#21--las-preguntas-de-arranque)
  sobre por qué son estas ocho preguntas y no más

**GameMaker y esta biblioteca**

- [13 · 14](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md)
  y [13 · 01 §8](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#8--el-documento-de-diseño-ligero),
  ya verificados con sus propias fuentes — este documento no repite esa verificación, construye
  encima
- `_indice/auditorias/r5-spec-driven.md` (8-sep-2026) — la auditoría que detectó, verificando los
  tres puntos de entrada de un agente a esta biblioteca (`SKILL.md`, `AGENTS.md §5`,
  `13 · 06 §2`), que ninguno obligaba a producir una especificación antes de crear el proyecto, y
  que encargó este documento junto con los pasos 0 añadidos a esos tres puntos de entrada

**Marcado con ⚠️.** Ninguna sección de este documento queda marcada: es metodología propia de esta
biblioteca para el caso de uso de un agente de IA construyendo con GameMaker, sin equivalente
directo en una fuente externa que citar para el método completo — solo sus dos piezas
verificables por separado (el coste de la ambigüedad tardía, y el núcleo mínimo de un brief de
encargo) llevan fuente primaria arriba.
