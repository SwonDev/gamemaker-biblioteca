# 16 · Progresión: árboles de habilidades, desbloqueos y meta-progresión

> Cómo se diseña **qué se desbloquea, en qué orden y a cambio de qué**: la forma del árbol de
> habilidades, el criterio para que un nodo merezca existir, el respec, y la meta-progresión
> entre partidas de un roguelite —cuánta antes de que el juego se gane solo, y el patrón de
> **monedas múltiples** que ya usas si has tocado [04 · 05](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md)
> sin haberlo visto nombrado. Cierra con el modelo de datos en GML —grafo de structs, validación
> de ciclos y alcanzabilidad por BFS, guardado versionado— y la UI navegable con mando.
>
> **Lo que NO cubre este documento** (y dónde está, para no repetirlo): las **fórmulas** de XP y
> niveles están en [13 · 13 §8](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#8--curvas-de-crecimiento-para-diseño)
> y el constructor `Progression` ya implementado en [04 · 04 §5.1](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md#51-niveles-y-curva-de-experiencia);
> aquí sólo se usan sus `skill_points`, no se repite cómo se calculan. El **pipeline de daño**
> —tipos, resistencias, armadura, escudos— es de [04 · 32](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md);
> aquí sólo se **engancha** un modificador, no se reescribe el pipeline. La **navegación de menús
> con mando** —foco, repetición, cuadrícula— es de [13 · 05 §2.2](./05%20-%20UI%20y%20UX%20de%20juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición);
> aquí se extiende a un **grafo libre**, que aquella sección no cubre. El **guardado** con
> versión de esquema es de [01 · 14 §9](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#9-sistema-de-guardado-completo-recomendado)
> y [`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml); aquí sólo se
> envuelve. La **economía general** (fuentes, sumideros, convertidores) es de
> [13 · 01 §4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#4--economía-y-balance).
> Y una moneda **premium** comprada con dinero real es tema de monetización, fuera de este
> documento: no hay ningún documento de esta biblioteca que lo cubra todavía.

---

## 1 · Los principios

### 1.1 Topologías de árbol, y qué comunica cada una

«Árbol de habilidades» es el nombre genérico, pero la forma real casi nunca es un árbol en el
sentido matemático (un único padre por nodo). La forma que elijas **es** el mensaje: le dice al
jugador, antes de leer una sola descripción, si va a especializarse, a explorar o a rellenar una
lista de la compra.

| Topología | Cómo se conecta | Qué comunica | Ejemplo verificado | Riesgo |
|---|---|---|---|---|
| **Lineal** | Un nodo, un padre, un hijo: una única secuencia | «Esto es inevitable, es cuestión de tiempo» | La curva de nivel de personaje pura, sin ramas (`Progression` de [04 · 04 §5.1](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md#51-niveles-y-curva-de-experiencia)) | Cero decisión: no es un árbol, es una barra de carga con pasos intermedios |
| **Ramificado (árbol propio)** | Cada nodo, salvo la raíz, tiene un único padre; un padre puede tener varios hijos | «Elige una identidad; no puedes tenerlo todo con los mismos puntos» | Estructura clásica de tres columnas por clase de *Diablo II* ⚠️ (citada de memoria, no abierta esta sesión) | Si una rama sale mejor que las otras, se vuelve «la correcta» y el resto decora (dominancia estratégica) |
| **Malla / red** | Un nodo puede tener varios padres; hay más de un camino hasta el mismo punto | «Aquí hay libertad total: el camino es tuyo, no el del diseñador» | *Path of Exile*: «a vast web of 1325 skills that provide passive bonuses to your character» — <https://www.pathofexile.com/passive-skill-tree> (consultado 2026-09-06) | Sin una herramienta externa para planificar la ruta, el jugador se pierde; hace falta un resumen de build en la propia UI |
| **Tablero / rejilla** | Nodos en una cuadrícula; te mueves ortogonalmente activando casillas | «El espacio se explora, no se memoriza; lo cercano cuesta menos que lo lejano» | *Final Fantasy X*, Sphere Grid: «a grid of interconnected nodes» que el personaje recorre gastando *Sphere Levels* — <https://en.wikipedia.org/wiki/Final_Fantasy_X> (consultado 2026-09-06) | Sesgo de anclaje: el nodo más cercano parece la única opción razonable aunque haya uno mejor tres pasos más allá |
| **Constelación / hub radial** | Varias sub-ramas alrededor de un punto de entrada compartido, sin la especialización de fábrica de la ramificada | «Empiezas neutral: la especialización la decides tú, no tu clase de partida» | *Final Fantasy X*, «Expert Sphere Grid»: **todos** los personajes arrancan en el nodo central del mismo grid, con menos nodos totales — misma fuente que arriba | El punto de entrada compartido puede converger en la misma build óptima para todo el mundo si no hay fricción de distancia real |
| **Piscina sin conexión** | Nodos sueltos, sin prerrequisitos entre sí; sólo un contador de nivel o de puntos los desbloquea | «Esto es un menú de opciones, no una identidad que construyes» | Perks de *shooter* multijugador tipo *Call of Duty* ⚠️ (citado de memoria, no abierto esta sesión) | Pierde el gancho de planificación a largo plazo: no hay «mapa» que mirar y soñar con la próxima ruta |

> 💡 **No hay una topología «correcta».** La malla da libertad pero exige una UI de resumen de
> build (§3.7); la ramificada da identidad clara pero corre el riesgo de la rama muerta; el
> tablero da exploración espacial pero necesita una cámara que se pueda mover (§3.6). Elige por
> lo que el juego necesita comunicar, no por la que has visto en el último juego que jugaste.

### 1.2 El criterio: un nodo que cambia cómo juegas vale por diez de +5 %

La página oficial del árbol de Path of Exile distingue dos categorías de nodo especial además
de los normales: *Notables* («bigger icons and offer specific bonuses to guide character
building») y **Keystones**, que según la misma fuente **«fundamentally change the way you
play, typically with one positive and one negative effect»** (<https://www.pathofexile.com/passive-skill-tree>,
consultado 2026-09-06).

Ese «positivo y negativo a la vez» es la parte que casi nadie copia y es la que hace el criterio
funcionar de verdad:

- Un nodo de **+5 % de daño** es invisible. El jugador no lo siente al golpear, sólo lo ve en una
  hoja de cálculo. Diez de ellos sí suman un número grande, pero la experiencia de jugar no
  cambia en ningún punto: sigues pulsando el mismo botón para el mismo resultado, un poco más
  fuerte.
- Un nodo que dice **«tu esquive ahora atraviesa enemigos, pero ya no da i-frames»** cambia una
  regla del juego. El jugador tiene una historia que contar («cojo esquives que atraviesan y
  aprendo a no necesitar los i-frames»), un riesgo real que asumir, y una razón para hablar de
  esa build en un foro.

**La regla de presupuesto**: por cada tramo (*tier*) del árbol, reserva **al menos un nodo que
cambie un verbo o una regla**, no sólo un número. El resto de nodos del tramo son relleno legítimo
—dan textura y hacen que el jugador tome micro-decisiones camino del nodo grande— pero nunca
deberían ser la única razón para entrar en una rama.

**El coste obligatorio.** Un nodo que cambia cómo juegas y **no** tiene contrapartida es, por
definición, estrictamente mejor que no cogerlo: deja de ser una decisión y se convierte en un
trámite que todo el mundo hace. La fuente oficial de Path of Exile es explícita en que sus
Keystones llevan **un efecto positivo y uno negativo**: eso es lo que los mantiene como
decisión y no como paso obligatorio. Diseña los tuyos igual: el nodo que da inmunidad al veneno a
cambio de no poder curarte por HoT (04 · 32 §4.7) es una Keystone; el que sólo añade inmunidad
sin nada a cambio es un error de diseño con forma de regalo.

### 1.3 Prerrequisitos: Y, O, coste en rama y nivel de personaje

Cuatro formas de exigir algo antes de un nodo, que se pueden combinar:

| Tipo | Regla | Para qué sirve |
|---|---|---|
| **Y (todos)** | Hacen falta *todos* los nodos listados | El camino normal de una ramificación: cada nodo exige el anterior |
| **O (cualquiera)** | Basta con *uno* de los listados | Confluencias: dos rutas que llegan al mismo nodo fuerte, típico de la topología de malla |
| **Coste en rama** | Hacen falta *N* puntos ya gastados en esa rama (no un nodo concreto) | Fuerza compromiso parcial con una identidad antes de dejar coger el nodo grande del fondo, sin fijar una ruta exacta dentro de la rama |
| **Nivel de personaje** | El nodo no se puede comprar hasta cierto nivel, aunque haya puntos | Sincroniza la potencia del árbol con la curva de dificultad general (13 · 01 §3.2): nadie llega a la Keystone en el minuto 5 |

El modelo de datos de §3.1 soporta los cuatro sin necesitar cuatro sistemas distintos: Y/O son un
campo del nodo, coste en rama y nivel son comprobaciones adicionales sobre el mismo grafo.

### 1.4 Coste: puntos, escalado y por qué casi nunca es una cifra fija

El caso simple es «cada nodo cuesta 1 punto de habilidad». Dos variaciones que aparecen en
cuanto el árbol crece:

- **Nodos de rango** (mejorables varias veces: «+1 armadura», comprable hasta 5 veces). Su coste
  **no** debe ser fijo: usa la curva **exponencial con razón baja** de
  [13 · 13 §8.3](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#83--cuál-para-qué) —la misma
  tabla dice que esa curva «es la que crea la decisión ¿ahorro o compro ya?»— en vez de una
  cuenta nueva. No se repite la fórmula aquí: `progresion_exponencial(_rango + 1, _coste_base, 1.15)`
  con la función ya definida en esa sección.
- **Nodos con coste en dos monedas** (puntos de habilidad + una moneda de partida, p. ej. oro):
  fuerza una segunda decisión —«tengo el punto, ¿tengo también el oro»— pero añade fricción de UI
  (dos números que mostrar, dos motivos posibles de bloqueo). Resérvalo para nodos poco frecuentes
  y de alto impacto; si lo aplicas a todos los nodos, has construido una tienda con forma de árbol.

### 1.5 Respec: las tres políticas, y cuál para qué género

La misma página oficial de Path of Exile confirma que el respec no es gratis por defecto: **«you
can also obtain respec points from quests or by finding rare items»** (fuente citada en §1.2).
Es una decisión de diseño, no un descuido: si reasignar cuesta cero, cada punto deja de ser una
apuesta y se convierte en una prueba sin riesgo.

| Política | Coste | Efecto en el jugador | Cuándo usarla |
|---|---|---|---|
| **Gratis, en cualquier momento** | Ninguno | Fomenta la experimentación; el árbol se siente como un menú de builds, no como una identidad | Roguelites (cada run empieza de cero de todos modos, §2.4) y juegos centrados en probar sinergias |
| **Limitado y con coste** | Un objeto raro, una moneda de meta-progresión, o sólo *N* veces por partida | El punto pesa: elegirlo mal duele, así que el jugador se lo piensa. Path of Exile usa exactamente esto | ARPG y juegos de progresión larga donde la identidad del personaje importa a lo largo de decenas de horas |
| **Nulo o casi nulo** | No se puede, salvo un evento narrativo puntual | La elección inicial es la más importante del juego; sin red de seguridad | Roguelike de permadeath puro (una sola vida por partida) o juegos que quieren que el jugador viva con su decisión ⚠️ (patrón de diseño citado de memoria, sin fuente concreta abierta esta sesión) |

**Regla práctica**: si tu árbol vive **dentro de una run** que se reinicia sola (roguelite, §2.4),
el respec gratis entre runs no cuesta nada porque la run siguiente ya parte de cero — la pregunta
del respec sólo importa **dentro** de la misma run, donde la respuesta casi siempre debería ser
«no» o «carísimo»: si puedes reasignar en mitad de una run sin coste, el árbol de esa run deja de
ser una apuesta y se convierte en una calculadora.

### 1.6 Builds: qué hace que una combinación de nodos SEA un build

Un build no es «los nodos que llevo»: es una **identidad jugable con un nombre que le pondrías en
una frase a un amigo** («voy de veneno que se cura con las pilas que acumula», «voy de escudo que
nunca se rompe pero pega flojísimo»). Dos o más nodos que se combinan generan un build cuando el
efecto conjunto **no es la suma de sus partes por separado**: el nodo de veneno con apilado
infinito (04 · 32 §2.3, `PoliticaApilado.APILAR`) más el nodo que cura por cada pila activa no son
dos bonificaciones sueltas, son una máquina.

**El antipatrón: la ruta dominante.** Si al terminar el árbol un jugador con calculadora puede
demostrar que una ruta es matemáticamente superior a cualquier otra en cualquier situación, el
resto del árbol es decoración cara. Esto no se detecta leyendo el árbol: se detecta simulando
combates o partidas con cada ruta candidata y comparando —el método de
[13 · 01 §4.4-4.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números)
(TTK, balancear en múltiplos) es el punto de partida; simular miles de combates con el `scr_pruebas`
de [13 · 10 §3.1](./10%20-%20Testing%20y%20QA.md#31-el-script-scr_pruebas) para leer distribución
en vez de un único cálculo a mano es el paso siguiente, y simularlo en serio con percentiles y
detección de dominancia ya tiene documento propio en
[13 · 21 §3.6](./21%20-%20Balance%20por%20simulación%20-%20Monte%20Carlo%2C%20Machinations%20y%20estrategias%20dominantes.md#36--cazar-dominancia-tasa-de-uso-frente-a-tasa-de-victoria)
(«Cazar dominancia: tasa de uso frente a tasa de victoria»).

### 1.7 Cuándo NO hace falta un grafo

No todo desbloqueo necesita prerrequisitos. Si tus «habilidades» son en realidad **una lista
plana de mejoras compradas por nivel o por moneda, sin que unas exijan otras**, no construyas un
grafo: usa la topología de **piscina sin conexión** de §1.1 y el modelo de datos se reduce a un
array de structs `{ id, nombre, coste, comprado }` sin campo `prerrequisitos`. Construir el grafo
completo de §3.1-§3.2 para una piscina sin conexión es trabajo que no vas a usar: la validación de
ciclos de un grafo sin aristas siempre pasa, y la de alcanzabilidad siempre dice que todo es
alcanzable. Guarda el grafo para cuando de verdad haya un «esto exige aquello».

---

## 2 · El método, paso a paso

### 2.1 Dibujar el árbol en papel: tramos, ganchos y una Keystone por rama

Antes de un JSON, una hoja o una pizarra:

1. **Divide el árbol en tramos** (tiers) por coste acumulado, no por posición visual: tramo 1 son
   los nodos alcanzables con los primeros 5 puntos, tramo 2 con los siguientes 10, etc.
2. **Da a cada rama un gancho de una frase** («la rama que convierte el escudo en arma»). Si no
   puedes escribir esa frase, la rama no tiene identidad todavía: son nodos sueltos con un color
   compartido.
3. **Coloca al menos una Keystone (§1.2) por rama**, normalmente al final del tramo 2 o al
   principio del 3: ni tan pronto que trivialice el resto del árbol, ni tan tarde que nadie
   llegue a verla en una partida normal.
4. **Cuenta los nodos de relleno por Keystone.** Una proporción sana suele rondar 3-5 nodos de
   `+stat` por cada nodo que cambia una regla; más de 8-10 y el jugador deja de leer las
   descripciones y empieza a comprar «lo más barato que tenga al lado».

### 2.2 Elegir la topología según el género

| Género | Topología recomendada | Por qué |
|---|---|---|
| Roguelite (meta-progresión, §2.4) | Piscina sin conexión, o malla poco densa | El jugador vuelve cientos de veces; una malla con 1000 nodos exige una UI de planificación que la mayoría de roguelites no necesitan |
| ARPG / Hack'n'slash | Malla o ramificado ancho | Sesiones largas, identidad de build central al *endgame*: la malla de Path of Exile es el caso de estudio |
| Metroidvania | Piscina o ramificado corto, casi siempre atado a **habilidades de movimiento**, no a stats | El árbol de habilidades ahí compite con el gating de mundo de [04 · 06](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md#8-cómo-escalarlo) (punto 3, «árbol de habilidades: permite elegir orden»): que no se pisen |
| RPG por turnos | Ramificado por clase, o tablero (Sphere Grid) si quieres romper la barrera de clases | El tablero permite que un mago llegue a nodos de guerrero pagando más pasos, sin romper el sistema de clases |
| Estrategia / gestión | Piscina, casi siempre atada a investigación con coste en una moneda de partida | El "árbol tecnológico" de estos juegos es una piscina con prerrequisitos Y, casi nunca una malla |

### 2.3 Presupuestar cobertura: el jugador que ya lo desbloqueó todo (D4)

Si un jugador dedicado puede comprar el 100 % del árbol en una sola partida, el árbol no es una
serie de decisiones: es una lista de tareas con orden libre. La cobertura sana para que la
elección siga importando **hasta el final** ronda el **60-75 % de los nodos totales** con los
puntos que da una partida completa: siempre queda algo fuera, y ese «algo» es lo que hace que dos
partidas de dos jugadores distintos se vean distintas.

Qué hacer con el jugador que, aun así, lo desbloquea todo (por farmear, por NG+, por jugar
cientos de horas):

- **Añade sumideros tardíos.** Es literalmente la regla de
  [13 · 01 §4.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#43--la-regla-que-evita-el-80--de-los-desastres-de-economía)
  aplicada al árbol en vez de a la economía: si los puntos (o la moneda de meta, §2.6) no tienen
  un sumidero al final del juego, se acumulan sin sentido. Cosméticos, modificadores de desafío,
  o una segunda capa de árbol de prestigio son sumideros legítimos.
- **New Game+ con multiplicadores**, exactamente la receta de
  [04 · 06 §8, punto 8](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md#8-cómo-escalarlo):
  como el estado del árbol es un struct, reescalar la dificultad es cambiarle los multiplicadores,
  no rehacer el árbol.
- **Acepta que un jugador de cientos de horas ha «terminado» el sistema.** No todo sumidero tiene
  que fingir que el árbol sigue siendo relevante para siempre: a veces la respuesta honesta es que
  el árbol cumplió su función durante la partida principal y el postgame vive de otros sistemas.

### 2.4 Meta-progresión de roguelite: cuánta, antes de que el juego se gane solo

La meta-progresión (mejoras que sobreviven a la muerte, frente al estado de la run que se pierde)
es casi universal en el roguelite moderno porque la muerte permanente pura genera abandono — la
razón exacta que ya da [04 · 05 §4.7](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md#47-muerte-permanente-y-meta-progresión).
Lo que ese documento no cubre —y es la pregunta que de verdad separa un roguelite bien calibrado
de uno que se rompe solo— es **cuánta**.

**El problema del poder acumulado.** Si la meta-progresión sólo da poder bruto (+HP máximo,
+daño base) sin límite, cada run sucesiva es objetivamente más fácil que la anterior con el mismo
esfuerzo del jugador. Pasadas suficientes runs, el contenido diseñado para una curva de
dificultad concreta ([13 · 01 §3.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#32--las-cuatro-formas-de-curva))
deja de suponer ningún reto: el juego se gana solo, no porque el jugador haya mejorado, sino
porque el personaje lo ha hecho por él. Es la misma lógica que la logarítmica de
[13 · 13 §8.2](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#82--las-cinco-curvas-a-diez-niveles)
recomienda para todo lo que **debe frenarse**: la meta-progresión de poder puro necesita techo, o
un roguelite deja de ser un roguelite y pasa a ser un incremental con estética de mazmorra.

### 2.5 Poder frente a opciones, y su efecto sobre la curva

La distinción que sí resuelve el problema de §2.4 es entre dos familias de meta-progresión:

- **Poder**: números que suben (más vida, más daño, más resistencia). Cada punto de poder
  **desplaza la curva de dificultad hacia abajo** sin que el diseñador lo haya decidido sala por
  sala: el reto que el nivel 3 tenía pensado para un personaje base ahora lo afronta un personaje
  ya reforzado.
- **Opciones**: cosas nuevas que se pueden **elegir**, no estadísticas que suben solas.
  *Hades* desbloquea el **Pact of Punishment** tras la primera victoria: un conjunto de
  modificadores de dificultad que el jugador activa **voluntariamente** a cambio de mejores
  recompensas, «to manually customize and increase the difficulty of the gameplay» y desbloquear
  «rare rewards after runs» y objetos decorativos —
  <https://en.wikipedia.org/wiki/Hades_(video_game)> (consultado 2026-09-06). La curva de
  dificultad no se mueve sola: **el jugador la mueve**, y sólo cuando quiere más reto.

**La regla:** la meta-progresión de opciones **no rompe** la curva de 13 · 01 §3.2 porque no
cambia la potencia del personaje contra un nivel fijo, cambia qué nivel afronta. La de poder sí la
rompe, así que si la usas, dale un **techo bajo y explícito** (el aumento total de poder entre la
run 1 y la run 100 no debería superar lo que un buen jugador gana con habilidad en la misma
franja) y complétala pronto con opciones, no sólo con más poder indefinido.

### 2.6 El patrón de monedas múltiples: partida frente a meta

`04 · 05 §5.8` ya implementa este patrón sin nombrarlo: `RunState.oro` es un campo que se **pierde
al morir**, y `MetaProgress.oro_total` es un campo que **se acumula para siempre** y se guarda en
disco. Son, de hecho, **dos monedas distintas** aunque compartan la palabra «oro» en el nombre:

| Moneda | Ámbito (dónde vive) | Se pierde al morir | Se gasta en | Ejemplo verificado |
|---|---|---|---|---|
| **De partida** | `RunState` | Sí | Tienda de la run, mejoras temporales que no sobreviven | `RunState.oro` — [04 · 05 §5.8](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md#58-run-state-y-meta-progresión) |
| **De meta** | `MetaProgress` (disco) | No | Desbloqueos permanentes, árbol de meta-progresión | `MetaProgress.oro_total` (misma fuente); *Dead Cells*: **Cells**, moneda persistente que «can be used to purchase permanent upgrades» y que si el jugador muere antes de gastarla «they lose all collected Cells» — <https://en.wikipedia.org/wiki/Dead_Cells> (consultado 2026-09-06) — nótese que en *Dead Cells* las Cells son la moneda de partida **hasta que se gastan**, y sólo entonces se vuelven meta: el corte no siempre es «un campo por moneda», a veces es «un momento de conversión» |
| **De prestigio** (opcional) | `MetaProgress` (disco) | No | Cosméticos, sumideros tardíos de §2.3 | ⚠️ patrón habitual del género, sin una fuente concreta abierta esta sesión para un ejemplo con nombre |

**Por qué el tipo de cambio nunca es bidireccional.** Si pudieras convertir moneda de meta de
vuelta a moneda de partida, cada muerte se volvería gratis en términos de progreso acumulado — se
rompe el riesgo que la muerte permanente pura debía comunicar en primer lugar (04 · 05 §4.7). La
conversión sólo circula en un sentido: partida → meta, nunca al revés. Generalizando lo que
`registrar_muerte()` ya hace línea a línea:

```gml
/// @func moneda_transferir_a_meta(_run, _meta, _campo_run, _campo_meta, _tasa = 1)
/// @desc Convierte parte de una moneda de PARTIDA en moneda de META. De un solo sentido:
///       nunca definas la función inversa. Generaliza lo que 04 · 05 §5.8 hace en línea con
///       `oro_total += _run.oro`, para cuando tengas más de una moneda que transferir.
/// @param {Struct} _run        p. ej. una instancia de RunState (04 · 05 §5.8)
/// @param {Struct} _meta       p. ej. una instancia de MetaProgress (04 · 05 §5.8)
/// @param {String} _campo_run  Nombre del campo en _run (p. ej. "oro")
/// @param {String} _campo_meta Nombre del campo en _meta (p. ej. "oro_total")
/// @param {Real}   _tasa       Cuánto de cada unidad de partida se convierte (1 = uno a uno)
/// @returns {Real}  Lo transferido, para mostrarlo en la pantalla de fin de run.
function moneda_transferir_a_meta(_run, _meta, _campo_run, _campo_meta, _tasa = 1)
{
    var _cantidad = variable_struct_exists(_run, _campo_run) ? _run[$ _campo_run] : 0;
    var _ganado   = floor(_cantidad * _tasa);

    var _actual = variable_struct_exists(_meta, _campo_meta) ? _meta[$ _campo_meta] : 0;
    _meta[$ _campo_meta] = _actual + _ganado;

    return _ganado;
}
```

### 2.7 Validar antes de programar: dos o tres builds a mano

Antes de escribir el JSON completo del árbol, simula **a mano** 2-3 rutas candidatas con la hoja
de cálculo de [13 · 01 §4.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#45--de-la-hoja-de-cálculo-al-juego):
¿cuántos puntos exige cada ruta hasta su Keystone? ¿se solapan nodos entre rutas «distintas» (si
todas pasan por los mismos 8 nodos base, no son rutas distintas, son la misma ruta con un adorno
al final)? Encontrar esto en una hoja de cálculo cuesta diez minutos; encontrarlo después de
programar la UI completa cuesta un día.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 El grafo de nodos: modelo de datos en JSON y carga a structs

Un nodo es dato puro. El JSON vive en Included Files, con el mismo patrón de lectura que
`resistencias_cargar()` en [04 · 32 §5.1](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#51-tipos-de-daño-y-tabla-de-resistencias):

```json
[
  { "id": "vitalidad_1", "nombre": "Vitalidad I", "tier": 1, "coste": 1,
    "prerrequisitos": [], "modo": 0,
    "efecto": { "tipo": 0, "campo": "defense", "valor": 3 },
    "pos": { "x": 0, "y": 0 } },

  { "id": "coraza_1", "nombre": "Coraza reforzada", "tier": 1, "coste": 1,
    "prerrequisitos": ["vitalidad_1"], "modo": 0,
    "efecto": { "tipo": 1, "valor": 8 },
    "pos": { "x": 1, "y": 0 } },

  { "id": "manto_ignifugo", "nombre": "Manto ignífugo", "tier": 2, "coste": 2,
    "prerrequisitos": ["coraza_1"], "modo": 0,
    "efecto": { "tipo": 2, "elemento": 1, "valor": -0.5 },
    "pos": { "x": 1, "y": 1 } },

  { "id": "sangre_furiosa", "nombre": "Sangre furiosa", "tier": 3, "coste": 3,
    "prerrequisitos": ["coraza_1", "manto_ignifugo"], "modo": 1,
    "efecto": { "tipo": 3, "flag": "sangre_furiosa" },
    "pos": { "x": 2, "y": 1 } }
]
```

`modo: 0` es «Y» (todos los prerrequisitos), `modo: 1` es «O» (cualquiera) — §1.3. `efecto.tipo`
indexa el enum `NodoEfecto` de abajo: `0` estadística, `1` armadura, `2` resistencia, `3`
habilidad (Keystone-flag). `sangre_furiosa` en el ejemplo es una Keystone real por el criterio de
§1.2: cambia una regla (inmunidad a interrupción mientras el combo dure), y en un proyecto
completo llevaría también su contrapartida negativa en el mismo `efecto` (p. ej. un multiplicador
de daño recibido) — se omite aquí para no alargar el ejemplo, no porque el criterio no aplique.

```gml
// ---------------------------------------------------------------------------
// scr_arbol_habilidades
// Verificado: buffer_load, buffer_read, buffer_string, buffer_delete, json_parse,
//             array_length, array_push, variable_struct_exists, struct_get_names,
//             file_exists, show_debug_message
// ---------------------------------------------------------------------------

/// Los cuatro tipos de efecto que un nodo puede aplicar. Ver §3.4 para dónde
/// engancha cada uno.
enum NodoEfecto { ESTADISTICA, ARMADURA, RESISTENCIA, HABILIDAD }

/// Y = hacen falta TODOS los prerrequisitos. O = basta con UNO. Ver §1.3.
enum PrerrequisitoModo { Y, O }

/// @func arbol_cargar(_archivo)
/// @desc Lee la definición del árbol desde un JSON de Included Files y construye
///       el grafo (nodos + adyacencia inversa). Sigue el patrón de lectura de
///       resistencias_cargar() (04 · 32 §5.1).
/// @param {String} _archivo  Ruta relativa al área de juego.
/// @returns {Struct}  Un ArbolHabilidades, o `undefined` si el archivo no existe.
function arbol_cargar(_archivo)
{
    if (!file_exists(_archivo))
    {
        show_debug_message($"arbol_cargar: no existe {_archivo}");
        return undefined;
    }

    var _buff = buffer_load(_archivo);
    var _json = buffer_read(_buff, buffer_string);
    buffer_delete(_buff);

    var _definiciones = json_parse(_json);   // array de nodos, como el ejemplo de arriba
    return arbol_construir(_definiciones);
}

/// @func arbol_construir(_definiciones)
/// @desc Construye el grafo a partir de un array de definiciones ya parseado.
///       Separado de arbol_cargar() para poder construir árboles en pruebas
///       (13 · 10 §3.1) sin tocar disco.
/// @param {Array<Struct>} _definiciones
/// @returns {Struct}  { nodos: {id: nodo}, raices: [ids sin prerrequisitos] }
function arbol_construir(_definiciones)
{
    var _nodos  = {};
    var _raices = [];

    // Paso 1: indexar cada nodo por id, y añadirle su lista de hijos (vacía).
    for (var _i = 0; _i < array_length(_definiciones); _i++)
    {
        var _d = _definiciones[_i];
        _d.hijos    = [];    // adyacencia inversa: se rellena en el paso 2
        _nodos[$ _d.id] = _d;

        if (array_length(_d.prerrequisitos) == 0) array_push(_raices, _d.id);
    }

    // Paso 2: para cada nodo, decirle a cada uno de sus prerrequisitos
    // "yo soy tu hijo". Esto es lo que permite recorrer el árbol hacia
    // adelante (§3.2, §3.6) sin recalcularlo cada vez.
    var _ids = struct_get_names(_nodos);
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _nodo = _nodos[$ _ids[_i]];
        for (var _j = 0; _j < array_length(_nodo.prerrequisitos); _j++)
        {
            var _padre_id = _nodo.prerrequisitos[_j];
            if (variable_struct_exists(_nodos, _padre_id))
            {
                array_push(_nodos[$ _padre_id].hijos, _nodo.id);
            }
        }
    }

    return { nodos: _nodos, raices: _raices };
}
```

### 3.2 Validación por grafo: ciclos (Kahn/BFS) y alcanzabilidad (BFS)

Dos preguntas, dos recorridos por anchura sobre el mismo grafo. **Ejecuta ambas al cargar el
árbol en desarrollo** (o como una prueba de `scr_pruebas`, 13 · 10 §3.1): un árbol con un ciclo
o con nodos huérfanos no debería llegar nunca a producción.

```gml
// ---------------------------------------------------------------------------
// scr_arbol_validar
// Verificado: array_length, array_push, array_shift NO EXISTE (no se usa: se
// recorre con un índice de cabeza en vez de desplazar el array — más barato),
// variable_struct_exists, struct_get_names, struct_set, is_undefined
// ---------------------------------------------------------------------------

/// @func arbol_detectar_ciclos(_arbol)
/// @desc Ordenación topológica de Kahn: BFS que procesa un nodo sólo cuando
///       TODOS sus prerrequisitos ya se procesaron. Si al final quedan nodos
///       sin procesar, esos nodos forman (o dependen de) un ciclo.
/// @param {Struct} _arbol  El devuelto por arbol_construir()/arbol_cargar().
/// @returns {Array<String>}  IDs en un ciclo. Vacío si el árbol es válido.
function arbol_detectar_ciclos(_arbol)
{
    var _ids = struct_get_names(_arbol.nodos);
    var _grado_entrada = {};   // cuántos prerrequisitos le faltan a cada nodo

    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _id = _ids[_i];
        _grado_entrada[$ _id] = array_length(_arbol.nodos[$ _id].prerrequisitos);
    }

    // La cola es un array con un índice de CABEZA, no un ds_queue: procesar
    // un array de unos pocos cientos de nodos es más barato que gestionar
    // una estructura aparte, y no hay que acordarse de destruirla.
    var _cola   = array_clone_ids(_arbol.raices);
    var _cabeza = 0;
    var _procesados = 0;

    while (_cabeza < array_length(_cola))
    {
        var _actual = _cola[_cabeza];
        _cabeza++;
        _procesados++;

        var _hijos = _arbol.nodos[$ _actual].hijos;
        for (var _i = 0; _i < array_length(_hijos); _i++)
        {
            var _hijo_id = _hijos[_i];
            _grado_entrada[$ _hijo_id]--;
            if (_grado_entrada[$ _hijo_id] == 0) array_push(_cola, _hijo_id);
        }
    }

    // Lo que Kahn NO pudo procesar tenía un grado de entrada que nunca llegó
    // a cero: está en un ciclo, o depende de un nodo que está en un ciclo.
    var _en_ciclo = [];
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        if (_grado_entrada[$ _ids[_i]] > 0) array_push(_en_ciclo, _ids[_i]);
    }
    return _en_ciclo;
}

/// @func array_clone_ids(_array)
/// @desc Copia superficial de un array de strings. GML copia arrays por valor
///       al asignarlos con "=", pero ser explícito aquí documenta la intención:
///       arbol_detectar_ciclos() NO debe mutar _arbol.raices.
function array_clone_ids(_array)
{
    var _copia = [];
    for (var _i = 0; _i < array_length(_array); _i++) array_push(_copia, _array[_i]);
    return _copia;
}

/// @func arbol_nodos_alcanzables(_arbol, _raices = undefined)
/// @desc BFS desde las raíces (o desde una lista propia, útil para comprobar
///       "¿qué se abre si ya tengo estos nodos?"). Un nodo con un prerrequisito
///       en modo O sólo necesita UNO de sus padres para ser alcanzable.
/// @param {Struct} _arbol
/// @param {Array<String>} _raices  Por defecto, _arbol.raices.
/// @returns {Struct}  Conjunto (struct usado como set) de ids alcanzables.
function arbol_nodos_alcanzables(_arbol, _raices = undefined)
{
    if (is_undefined(_raices)) _raices = _arbol.raices;

    var _visitados = {};
    var _cola      = array_clone_ids(_raices);
    var _cabeza    = 0;

    for (var _i = 0; _i < array_length(_cola); _i++) _visitados[$ _cola[_i]] = true;

    while (_cabeza < array_length(_cola))
    {
        var _actual_id = _cola[_cabeza];
        _cabeza++;

        var _hijos = _arbol.nodos[$ _actual_id].hijos;
        for (var _i = 0; _i < array_length(_hijos); _i++)
        {
            var _hijo_id = _hijos[_i];
            if (variable_struct_exists(_visitados, _hijo_id)) continue;   // ya visitado

            var _hijo = _arbol.nodos[$ _hijo_id];
            var _entra;

            if (_hijo.modo == PrerrequisitoModo.O)
            {
                // Con UN padre alcanzado ya basta.
                _entra = true;
            }
            else
            {
                // Modo Y: hacen falta TODOS los prerrequisitos del hijo.
                _entra = true;
                for (var _p = 0; _p < array_length(_hijo.prerrequisitos); _p++)
                {
                    if (!variable_struct_exists(_visitados, _hijo.prerrequisitos[_p]))
                    {
                        _entra = false;
                        break;
                    }
                }
            }

            if (_entra)
            {
                _visitados[$ _hijo_id] = true;
                array_push(_cola, _hijo_id);
            }
        }
    }
    return _visitados;
}

/// @func arbol_validar(_arbol)
/// @desc Junta las dos comprobaciones. Llámala al cargar el árbol en desarrollo,
///       o envuélvela en una prueba de scr_pruebas (13 · 10 §3.1).
/// @returns {Struct}  { valido: Bool, ciclos: Array<String>, huerfanos: Array<String> }
function arbol_validar(_arbol)
{
    var _ciclos = arbol_detectar_ciclos(_arbol);

    var _alcanzables = arbol_nodos_alcanzables(_arbol);
    var _ids = struct_get_names(_arbol.nodos);
    var _huerfanos = [];
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        if (!variable_struct_exists(_alcanzables, _ids[_i])) array_push(_huerfanos, _ids[_i]);
    }

    var _valido = (array_length(_ciclos) == 0) && (array_length(_huerfanos) == 0);

    if (!_valido)
    {
        show_debug_message($"arbol_validar: {array_length(_ciclos)} nodo(s) en ciclo, "
                          + $"{array_length(_huerfanos)} nodo(s) inalcanzable(s)");
    }

    return { valido: _valido, ciclos: _ciclos, huerfanos: _huerfanos };
}
```

> 🔺 **Un nodo en modo O que sólo tiene UN prerrequisito se comporta igual en Y y en O.** La
> diferencia sólo aparece con dos o más prerrequisitos. Si tu editor de datos permite escribir
> `modo: 1` con un único prerrequisito, no es un bug, simplemente es indistinguible — no hace
> falta una regla de validación extra para ese caso.
>
> 💡 **Por qué BFS y no DFS aquí.** Para alcanzabilidad, cualquiera de los dos recorridos da el
> mismo conjunto final: lo que importa es visitar cada nodo una vez, no el orden. Se usa BFS
> (cola con índice de cabeza) en vez de DFS (pila, como el `array_pop` de
> [04 · 05 §5.4](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md#54-validación-por-flood-fill))
> porque Kahn **necesita** procesar en orden de grado de entrada creciente para que la detección
> de ciclos sea correcta, y reutilizar el mismo patrón de recorrido en las dos funciones deja el
> script más fácil de leer que mezclar una pila en una y una cola en la otra.

### 3.3 Comprar, revertir y el respec completo

El estado de compra es **por partida/perfil**, no por definición del árbol: dos personajes pueden
compartir el mismo `ArbolHabilidades` (de §3.1) con `EstadoArbol` distintos.

```gml
// ---------------------------------------------------------------------------
// scr_estado_arbol
// Verificado: variable_struct_exists, struct_get_names, array_length, array_push,
//             array_delete, array_contains
// ---------------------------------------------------------------------------

/// @func EstadoArbol(_puntos_iniciales = 0)
/// @desc El progreso de UN jugador/personaje sobre un ArbolHabilidades.
function EstadoArbol(_puntos_iniciales = 0) constructor
{
    puntos_disponibles = _puntos_iniciales;
    comprados          = {};    // conjunto: { id: true, ... }
    orden_compra       = [];    // en qué orden se compró cada nodo — lo exige el respec

    /// @desc ¿Se puede comprar este nodo AHORA MISMO? Comprueba puntos,
    ///       prerrequisitos (Y/O, §1.3) y que no esté ya comprado.
    puede_comprar = function(_arbol, _id)
    {
        if (variable_struct_exists(comprados, _id)) return false;

        var _nodo = _arbol.nodos[$ _id];
        if (puntos_disponibles < _nodo.coste) return false;

        if (array_length(_nodo.prerrequisitos) == 0) return true;   // nodo raíz

        if (_nodo.modo == PrerrequisitoModo.O)
        {
            for (var _i = 0; _i < array_length(_nodo.prerrequisitos); _i++)
            {
                if (variable_struct_exists(comprados, _nodo.prerrequisitos[_i])) return true;
            }
            return false;
        }
        else   // Y: todos
        {
            for (var _i = 0; _i < array_length(_nodo.prerrequisitos); _i++)
            {
                if (!variable_struct_exists(comprados, _nodo.prerrequisitos[_i])) return false;
            }
            return true;
        }
    };

    /// @desc Compra un nodo y aplica su efecto (§3.4). Devuelve el motivo del
    ///       fallo si no se pudo, para que la UI lo enseñe (§3.7, siguiendo el
    ///       patrón "motivo" de boton_nuevo(), 13 · 05 §3.5a).
    comprar = function(_arbol, _id, _stats, _combate)
    {
        if (!puede_comprar(_arbol, _id)) return { ok: false, motivo: "No se cumplen los requisitos" };

        var _nodo = _arbol.nodos[$ _id];
        puntos_disponibles -= _nodo.coste;
        comprados[$ _id] = true;
        array_push(orden_compra, _id);

        nodo_efecto_aplicar(_nodo, _stats, _combate);
        return { ok: true, motivo: "" };
    };

    /// @desc Deshace UN nodo y le devuelve sus puntos, sólo si ningún nodo
    ///       comprado depende de él (comprobación simple: ¿algún hijo suyo
    ///       está comprado?). Es la pieza que usa respec_completo().
    revertir = function(_arbol, _id, _stats, _combate)
    {
        if (!variable_struct_exists(comprados, _id)) return false;

        var _nodo  = _arbol.nodos[$ _id];
        var _hijos = _nodo.hijos;
        for (var _i = 0; _i < array_length(_hijos); _i++)
        {
            if (variable_struct_exists(comprados, _hijos[_i])) return false;   // hay dependientes
        }

        nodo_efecto_revertir(_nodo, _stats, _combate);
        struct_remove(comprados, _id);
        puntos_disponibles += _nodo.coste;

        var _pos = array_find_index(orden_compra, function(_v, _i, _id_buscado) { return _v == _id_buscado; }, 0, array_length(orden_compra), _id);
        if (_pos != -1) array_delete(orden_compra, _pos, 1);
        return true;
    };

    /// @desc Respec completo: revierte TODOS los nodos en el orden INVERSO al
    ///       que se compraron. El orden inverso garantiza que nunca se intenta
    ///       revertir un nodo mientras un hijo suyo sigue comprado.
    respec_completo = function(_arbol, _stats, _combate)
    {
        var _copia = array_clone_ids(orden_compra);
        for (var _i = array_length(_copia) - 1; _i >= 0; _i--)
        {
            revertir(_arbol, _copia[_i], _stats, _combate);
        }
    };

    serializar = function()
    {
        return { puntos_disponibles: puntos_disponibles, comprados: comprados,
                 orden_compra: orden_compra };
    };

    static deserializar = function(_d)
    {
        var _e = new EstadoArbol(_d.puntos_disponibles);
        _e.comprados    = _d.comprados;
        _e.orden_compra = _d.orden_compra;
        return _e;
    };
}
```

`array_find_index` recibe una función y un valor extra por argumento posicional final
(`array_find_index(array, function, [offset], [length])`, verificado con `buscar.py`); aquí se usa
para localizar la posición de `_id` dentro de `orden_compra` sin escribir un bucle manual.
`struct_remove(struct, name)` (verificado con `buscar.py`, devuelve `Undefined`) quita un campo de
un struct por nombre: es la función que borra un id de `comprados` al revertir un nodo.

### 3.4 Enganchar los efectos: estadísticas, armadura, resistencias y Keystones

Esta es la sección que el encargo pide explícitamente: **los bonos se aplican como modificadores
enganchados al sistema de daño de [04 · 32](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)**,
no como un sistema de stats paralelo. Cada tipo de `NodoEfecto` (§3.1) escribe en un sitio ya
existente y ya documentado:

| `NodoEfecto` | Dónde escribe | Documento que lo define |
|---|---|---|
| `ESTADISTICA` | `Stats.mods.<campo>` (ataque, defensa, velocidad) | [04 · 04 §5.0](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md#50-estadísticas) |
| `ARMADURA` | `combate.armadura` | [04 · 32 §5.2](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#52-armadura) |
| `RESISTENCIA` | `combate.resistencias.<tipo>` | [04 · 32 §5.1](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#51-tipos-de-daño-y-tabla-de-resistencias) |
| `HABILIDAD` (Keystone) | `global.progreso.<flag>` | [13 · 01 §5.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#53--gating-la-mecánica-no-aparece-hasta-que-la-anterior-está-probada) |

La última fila es la conexión menos obvia y la más útil: una Keystone que **cambia una regla**
(§1.2) es, mecánicamente, **la misma idea que un flag de gating** — sólo que en vez de
desbloquearse al encontrar un objeto en el mundo, se desbloquea al gastar puntos. Reutilizar
`global.progreso` en vez de inventar un segundo sistema de flags significa que el resto de tu
código —el que ya comprueba `contenido_permitido("dash")`— no necesita saber si el jugador
consiguió el dash explorando o comprándolo en el árbol.

```gml
// ---------------------------------------------------------------------------
// scr_nodo_efecto
// Verificado: variable_struct_exists, dano_tipo_a_clave (04 · 32 §5.1, no es
// del runtime: es código de esta biblioteca)
// ---------------------------------------------------------------------------

/// @func nodo_efecto_aplicar(_nodo, _stats, _combate)
/// @desc Aplica el efecto de un nodo YA comprado. Todos los efectos son
///       ADITIVOS a propósito (§3.4 nota de abajo): así revertir es sólo
///       restar lo mismo que se sumó, sin guardar un valor "antes de".
function nodo_efecto_aplicar(_nodo, _stats, _combate)
{
    var _ef = _nodo.efecto;
    switch (_ef.tipo)
    {
        case NodoEfecto.ESTADISTICA:
            _stats.mods[$ _ef.campo] += _ef.valor;                        // 04 · 04 §5.0
            break;

        case NodoEfecto.ARMADURA:
            _combate.armadura += _ef.valor;                               // 04 · 32 §5.2
            break;

        case NodoEfecto.RESISTENCIA:
            var _clave = dano_tipo_a_clave(_ef.elemento);                 // 04 · 32 §5.1
            var _actual = variable_struct_exists(_combate.resistencias, _clave)
                        ? _combate.resistencias[$ _clave] : 1.0;
            _combate.resistencias[$ _clave] = _actual + _ef.valor;
            break;

        case NodoEfecto.HABILIDAD:
            if (!variable_global_exists("progreso")) global.progreso = {};
            global.progreso[$ _ef.flag] = true;                           // 13 · 01 §5.3
            break;
    }
}

/// @func nodo_efecto_revertir(_nodo, _stats, _combate)
/// @desc El inverso exacto de nodo_efecto_aplicar(). Existe SÓLO porque todos
///       los efectos son sumas/restas simples — nunca multiplicaciones ni
///       "fijar a un valor": eso rompería la reversibilidad y el respec
///       tendría que guardar el historial completo en vez de sólo el orden.
function nodo_efecto_revertir(_nodo, _stats, _combate)
{
    var _ef = _nodo.efecto;
    switch (_ef.tipo)
    {
        case NodoEfecto.ESTADISTICA:
            _stats.mods[$ _ef.campo] -= _ef.valor;
            break;

        case NodoEfecto.ARMADURA:
            _combate.armadura -= _ef.valor;
            break;

        case NodoEfecto.RESISTENCIA:
            var _clave = dano_tipo_a_clave(_ef.elemento);
            _combate.resistencias[$ _clave] -= _ef.valor;
            break;

        case NodoEfecto.HABILIDAD:
            if (variable_global_exists("progreso")) global.progreso[$ _ef.flag] = false;
            break;
    }
}
```

> 🔺 **Diseña TODOS los efectos como sumas o restas planas, nunca como multiplicadores
> compuestos ni como «fijar a X».** Si un nodo hiciera `_combate.armadura *= 1.2`, revertirlo
> exigiría dividir por 1.2 — y si dos nodos multiplicativos se compran en un orden y se revierten
> en otro, el resultado depende del orden por errores de redondeo. La suma no tiene ese problema:
> `+8` seguido de `-8` es exactamente el valor de partida, en cualquier orden. Si de verdad
> necesitas un nodo multiplicativo (raro, pero existe: «+50 % de armadura total»), recalcúlalo
> desde cero a partir de la lista de `comprados` en vez de mutar el campo in situ.
>
> 💡 Después de `nodo_efecto_aplicar()` sobre un `ARMADURA` o `RESISTENCIA`, si tu proyecto usa
> `Stats.refresh()` (04 · 04 §5.0) para recalcular `hp_max` tras cambios de equipo, llama también
> a esa función: un nodo de vitalidad que suba `hp_base` necesita el mismo recálculo que subir de
> nivel.

### 3.5 Meta-progresión persistente: guardado versionado

El estado del árbol (`EstadoArbol`, por partida) y la meta-progresión (`MetaProgress`, entre
partidas) se guardan con las funciones ya existentes de
[`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) — no hay que reescribir
`save_game`/`load_game`, sólo decidir qué va en el sobre de datos:

```gml
/// obj_meta · al terminar una run (morir o completarla) ------------------
var _ganado = moneda_transferir_a_meta(global.run, global.meta, "oro", "oro_total");

var _datos_meta = {
    meta_progreso : global.meta.serializar(),        // MetaProgress, 04 · 05 §5.8
    arbol_meta    : global.arbol_meta_estado.serializar()   // EstadoArbol de meta-progresión
};

if (!save_game("meta", _datos_meta))
{
    show_debug_message("No se pudo guardar la meta-progresión: el jugador la perdería al cerrar.");
}
```

```gml
/// obj_arranque · Create --------------------------------------------------
if (save_exists("meta"))
{
    var _datos = load_game("meta");                  // aplica migración si hace falta (ver abajo)
    global.meta            = MetaProgress.deserializar(_datos.meta_progreso);
    global.arbol_meta_estado = EstadoArbol.deserializar(_datos.arbol_meta);
}
else
{
    global.meta              = new MetaProgress();
    global.arbol_meta_estado = new EstadoArbol(0);
}
```

**La migración que vas a necesitar seguro**: añadir un nodo nuevo al árbol no rompe nada (un save
viejo simplemente no lo tiene en `comprados`), pero **quitar o renombrar un nodo sí**. Un save
viejo con un id en `comprados` que ya no existe en el `ArbolHabilidades` actual debe limpiarse al
cargar, con el mismo criterio que
[04 · 06, checklist de errores](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md#7-errores-clásicos-y-cómo-evitarlos)
ya da para las habilidades del mundo: **copia clave por clave**, no confíes en el struct entero.

```gml
/// @func arbol_estado_limpiar_ids_muertos(_estado, _arbol)
/// @desc Quita de `comprados` cualquier id que ya no exista en el árbol actual.
///       Los puntos gastados en un nodo eliminado NO se devuelven (decisión de
///       diseño: es más simple y no crea puntos gratis; documenta la excepción
///       si tu proyecto prefiere devolverlos).
function arbol_estado_limpiar_ids_muertos(_estado, _arbol)
{
    var _ids_comprados = struct_get_names(_estado.comprados);
    for (var _i = 0; _i < array_length(_ids_comprados); _i++)
    {
        var _id = _ids_comprados[_i];
        if (!variable_struct_exists(_arbol.nodos, _id))
        {
            struct_remove(_estado.comprados, _id);   // 04 · 06 §7 — copia clave por clave, no confíes en el struct entero
        }
    }
}
```

Define `global.save_migrar` (el hook que ya espera `load_game()`, 06/`scr_save_load.gml`) para
que esta limpieza sea automática en vez de una llamada que alguien se puede olvidar:

```gml
global.save_migrar = function(_datos, _version_vieja)
{
    // v1 → v2: se retiró el nodo "furia_antigua" del árbol de meta-progresión.
    if (_version_vieja < 2 && struct_exists(_datos, "arbol_meta"))
    {
        struct_remove(_datos.arbol_meta.comprados, "furia_antigua");
    }
    return _datos;
};
```

### 3.6 UI navegable con mando: foco en un grafo libre

[13 · 05 §2.2](./05%20-%20UI%20y%20UX%20de%20juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición)
resuelve listas y cuadrículas con `foco_rejilla()` — úsala tal cual si tu árbol es un tablero
(§1.1). Lo que esa sección **no** cubre es un grafo con posiciones libres (malla, ramificado): ahí
«arriba» no es una fila, es una dirección en el espacio, y el nodo correcto al pulsar arriba es el
vecino conectado cuyo ángulo se parece más a «arriba».

```gml
// ---------------------------------------------------------------------------
// scr_arbol_foco
// Verificado: point_direction, angle_difference, array_length, array_push,
//             variable_struct_exists
// Reutiliza repeticion_paso() y repeticion_nueva() de 13 · 05 §2.2 SIN
// reescribirlos: sólo se define la parte que aquella sección no cubre.
// ---------------------------------------------------------------------------

/// @func arbol_vecinos(_arbol, _id)
/// @desc Nodos conectados a uno: sus prerrequisitos MÁS sus hijos. La
///       navegación de un grafo va en las dos direcciones, no sólo hacia
///       adelante.
/// @returns {Array<String>}
function arbol_vecinos(_arbol, _id)
{
    var _nodo = _arbol.nodos[$ _id];
    var _vecinos = array_clone_ids(_nodo.prerrequisitos);
    for (var _i = 0; _i < array_length(_nodo.hijos); _i++) array_push(_vecinos, _nodo.hijos[_i]);
    return _vecinos;
}

/// @func arbol_foco_mover(_arbol, _foco_actual, _dx, _dy)
/// @desc Mueve el foco al vecino conectado cuyo ángulo se parece más a la
///       dirección pulsada. Si ningún vecino cae dentro de un cono de 100°
///       alrededor de esa dirección, el foco NO se mueve — mejor quieto que
///       saltar a un nodo que el jugador no esperaba.
/// @param {Struct} _arbol
/// @param {String} _foco_actual  Id del nodo con foco.
/// @param {Real}   _dx, _dy      Dirección pulsada, en coordenadas de pantalla
///                               (_dy negativo = arriba, como en GameMaker).
/// @returns {String}  El id con foco tras el movimiento (puede ser el mismo).
function arbol_foco_mover(_arbol, _foco_actual, _dx, _dy)
{
    if (_dx == 0 && _dy == 0) return _foco_actual;

    var _nodo_actual  = _arbol.nodos[$ _foco_actual];
    var _ang_deseado  = point_direction(0, 0, _dx, -_dy);   // -_dy: Y de pantalla crece hacia abajo
    var _vecinos      = arbol_vecinos(_arbol, _foco_actual);

    var _mejor_id  = _foco_actual;
    var _mejor_dif = 50;   // medio cono de 100°: por encima de esto, se descarta

    for (var _i = 0; _i < array_length(_vecinos); _i++)
    {
        var _vecino = _arbol.nodos[$ _vecinos[_i]];
        var _ang_vecino = point_direction(_nodo_actual.pos.x, _nodo_actual.pos.y,
                                          _vecino.pos.x,      _vecino.pos.y);
        var _dif = abs(angle_difference(_ang_deseado, _ang_vecino));

        if (_dif < _mejor_dif)
        {
            _mejor_dif = _dif;
            _mejor_id  = _vecino.id;
        }
    }

    return _mejor_id;
}
```

```gml
/// obj_ui_arbol · Create
foco_id   = global.arbol_actual.raices[0];    // arranca en la primera raíz
rep_izq   = repeticion_nueva();               // 13 · 05 §2.2 — sin redefinir
rep_der   = repeticion_nueva();
rep_arr   = repeticion_nueva();
rep_aba   = repeticion_nueva();

/// obj_ui_arbol · Step
var _zm = 0.5;   // misma zona muerta alta que 13 · 05 §2.2, por el mismo motivo
var _der = keyboard_check(vk_right) || gamepad_button_check(0, gp_padr) || gamepad_axis_value(0, gp_axislh) >  _zm;
var _izq = keyboard_check(vk_left)  || gamepad_button_check(0, gp_padl) || gamepad_axis_value(0, gp_axislh) < -_zm;
var _aba = keyboard_check(vk_down)  || gamepad_button_check(0, gp_padd) || gamepad_axis_value(0, gp_axislv) >  _zm;
var _arr = keyboard_check(vk_up)    || gamepad_button_check(0, gp_padu) || gamepad_axis_value(0, gp_axislv) < -_zm;

if (repeticion_paso(rep_der, _der)) foco_id = arbol_foco_mover(global.arbol_actual, foco_id,  1,  0);
if (repeticion_paso(rep_izq, _izq)) foco_id = arbol_foco_mover(global.arbol_actual, foco_id, -1,  0);
if (repeticion_paso(rep_aba, _aba)) foco_id = arbol_foco_mover(global.arbol_actual, foco_id,  0,  1);
if (repeticion_paso(rep_arr, _arr)) foco_id = arbol_foco_mover(global.arbol_actual, foco_id,  0, -1);

if (keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(0, gp_face1))
{
    var _resultado = global.estado_arbol.comprar(global.arbol_actual, foco_id, global.player_stats, obj_jugador.combate);
    if (!_resultado.ok) aviso_lanzar(_resultado.motivo, "error");   // 13 · 05 §3.5a, mismo patrón
}
```

> 🔺 **A diferencia del gating en el mundo** (13 · 02 §1.4, donde «el gate dice que falta algo,
> no qué falta», para proteger el descubrimiento), **en el menú del árbol sí debes decir
> exactamente qué falta**: «Necesitas: Coraza reforzada» o «Te faltan 2 puntos». Aquí no hay
> descubrimiento que proteger — sólo fricción de interfaz que evitar. Confundir estas dos reglas
> en direcciones opuestas es un error real: un cartel en el mundo que deletrea la solución mata el
> «ajá»; un árbol de habilidades que oculta por qué un nodo está bloqueado sólo genera tickets de
> soporte.

### 3.7 Dibujar el árbol: nodos, conexiones y estado visual

Reutiliza el panel nine-slice de
[13 · 05 §3.4](./05%20-%20UI%20y%20UX%20de%20juego.md#34-paneles-nine-slice-un-sprite-pequeño-para-cualquier-tamaño)
(`panel_dibujar()`) para el fondo de cada nodo y el tooltip de
[13 · 05 §3.5d](./05%20-%20UI%20y%20UX%20de%20juego.md#d-tooltip-el-que-siempre-se-sale-de-la-pantalla)
(`pista_dibujar()`) para su descripción — no se reescriben aquí.

```gml
// ---------------------------------------------------------------------------
// scr_arbol_dibujar
// Verificado: draw_line_width, draw_sprite_ext, draw_set_color, draw_set_halign,
//             draw_set_valign, fa_center, fa_middle, c_white, c_gray, c_green,
//             merge_colour
// ---------------------------------------------------------------------------

/// @func nodo_color_estado(_id, _estado, _arbol)
/// @desc Tres estados visuales, siguiendo el principio de affordance de
///       13 · 05 §1.6: el color solo, sin texto, debe decir si un nodo se
///       puede tocar.
/// @returns {Real}  Un color de GameMaker.
function nodo_color_estado(_id, _estado, _arbol)
{
    if (variable_struct_exists(_estado.comprados, _id)) return c_green;          // comprado
    if (_estado.puede_comprar(_arbol, _id))             return c_white;          // disponible
    return c_gray;                                                                // bloqueado
}

/// @func arbol_dibujar(_arbol, _estado, _foco_id, _offset_x, _offset_y, _escala = 48)
/// @desc Dibuja conexiones primero (para que queden DEBAJO de los nodos) y
///       luego cada nodo como un panel con icono. _offset sirve de cámara:
///       súmale la posición del foco con signo negativo para que el grafo
///       "siga" al foco, igual que un scroll de lista (04 · 18) pero en 2D.
function arbol_dibujar(_arbol, _estado, _foco_id, _offset_x, _offset_y, _escala = 48)
{
    var _ids = struct_get_names(_arbol.nodos);

    // --- Conexiones -----------------------------------------------------
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _nodo = _arbol.nodos[$ _ids[_i]];
        var _px1  = _offset_x + _nodo.pos.x * _escala;
        var _py1  = _offset_y + _nodo.pos.y * _escala;

        for (var _j = 0; _j < array_length(_nodo.prerrequisitos); _j++)
        {
            var _padre = _arbol.nodos[$ _nodo.prerrequisitos[_j]];
            var _px2   = _offset_x + _padre.pos.x * _escala;
            var _py2   = _offset_y + _padre.pos.y * _escala;

            var _ambos_comprados = variable_struct_exists(_estado.comprados, _nodo.id)
                                 && variable_struct_exists(_estado.comprados, _padre.id);
            draw_set_color(_ambos_comprados ? c_green : c_gray);
            draw_line_width(_px1, _py1, _px2, _py2, _ambos_comprados ? 3 : 1);
        }
    }

    // --- Nodos ------------------------------------------------------------
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _nodo = _arbol.nodos[$ _ids[_i]];
        var _px   = _offset_x + _nodo.pos.x * _escala;
        var _py   = _offset_y + _nodo.pos.y * _escala;
        var _col  = nodo_color_estado(_nodo.id, _estado, _arbol);

        panel_dibujar(spr_panel_nodo, _px - 16, _py - 16, 32, 32, _col, 1);   // 13 · 05 §3.4

        if (_nodo.id == _foco_id)
        {
            draw_set_color(c_white);
            draw_rectangle(_px - 19, _py - 19, _px + 19, _py + 19, true);   // marco de foco
        }
    }

    // --- Tooltip del nodo con foco -----------------------------------------
    var _f = _arbol.nodos[$ _foco_id];
    var _texto = $"{_f.nombre}\nCoste: {_f.coste}";
    if (!_estado.puede_comprar(_arbol, _foco_id) && !variable_struct_exists(_estado.comprados, _foco_id))
    {
        _texto += "\n(bloqueado: faltan requisitos o puntos)";
    }
    pista_dibujar(_texto, _offset_x + _f.pos.x * _escala, _offset_y + _f.pos.y * _escala);   // 13 · 05 §3.5d
}
```

### 3.8 Telemetría de progresión

Extiende `telemetria_registrar()` de
[13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json)
con tres eventos propios de progresión — sin reescribir la función, sólo llamándola con tipos
nuevos:

```gml
// Al comprar un nodo:
telemetria_registrar("nodo_comprado", { id: foco_id, coste: _nodo.coste,
                                          puntos_restantes: global.estado_arbol.puntos_disponibles });

// Al hacer un respec completo:
telemetria_registrar("respec", { nodos_revertidos: array_length(global.estado_arbol.orden_compra) });

// Al terminar una run con meta-progresión:
telemetria_registrar("run_fin", { oro_transferido: _ganado, piso_alcanzado: global.run.piso });
```

Con eso, la misma consulta de `jq` que 13 · 01 §9.6 usa para «¿qué sala mata más?» responde
también «¿qué nodo compra todo el mundo primero?» y «¿cuánta gente hace respec, y en qué run?» —
la señal que de verdad dice si tu árbol tiene una ruta dominante (§1.6) sin necesitar simulación:
si el 95 % de las partidas compran los mismos 6 nodos en el mismo orden, no hace falta Monte Carlo
para saber que el resto del árbol no se está usando.

---

## 4 · Checklist

- [ ] Cada rama tiene una frase que la describe, y al menos una Keystone (§1.2) con contrapartida
      negativa real, no sólo positiva.
- [ ] La cobertura del árbol con los puntos de una partida completa está entre el 60 % y el 75 %
      (§2.3) — si es 100 %, no es un árbol, es una lista de tareas.
- [ ] El respec tiene una política decidida a propósito (§1.5), no «lo que hizo el motor por
      defecto».
- [ ] Todo `NodoEfecto` es aditivo (suma/resta), nunca multiplicativo ni «fijar a X» (§3.4) — si
      no puedes revertirlo con la operación inversa exacta, el respec se rompe.
- [ ] `arbol_validar()` (§3.2) se ejecuta sin ciclos ni huérfanos antes de cada build.
- [ ] La meta-progresión tiene un techo de poder explícito, o se apoya en opciones en vez de sólo
      en poder (§2.4-§2.5).
- [ ] Las monedas de partida y de meta están en campos distintos, y la conversión entre ellas es
      de un solo sentido (§2.6).
- [ ] El guardado de la meta-progresión tiene versión de esquema y una función
      `global.save_migrar` que limpia ids de nodos retirados (§3.5).
- [ ] La navegación con mando siempre tiene un nodo con foco (regla 1 de las cinco leyes del
      foco, 13 · 05 §2.2), y ese foco sobrevive a salir y volver a entrar en la pantalla.
- [ ] Cada nodo bloqueado dice **por qué** está bloqueado, con texto explícito — al contrario que
      el gating de mundo (§3.6).

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| Árbol lleno de nodos de `+5 %` sin ninguna Keystone | Es lo más rápido de rellenar en una hoja de cálculo | Presupuesta al menos un nodo de regla-cambiada por rama antes de rellenar con stats (§1.2, §2.1) |
| El 100 % del árbol se desbloquea en una partida normal | Nadie calculó la cobertura, sólo el número total de nodos | Calcula puntos totales esperados ÷ coste medio y ajusta hasta el 60-75 % (§2.3) |
| Respec gratis e ilimitado en un juego de progresión larga | Parece "amigable con el jugador" y es fácil de programar | Decide la política a propósito con la tabla de §1.5; gratis sólo si el árbol se reinicia solo (roguelite) |
| Meta-progresión de sólo poder, sin techo | Es lo primero que se le ocurre a todo el mundo: "más vida al morir" | Añade opciones (§2.5) y un techo explícito de poder total acumulable |
| Convertir moneda de meta de vuelta a moneda de partida "para que el jugador no se quede atascado" | Parece un rescate razonable en una run difícil | Si hace falta un rescate, dalo como opción de dificultad (Pact of Punishment, §2.5), nunca deshaciendo la separación de monedas (§2.6) |
| Guardar `comprados` como el struct de nodos completo en vez de sólo los ids | Es más cómodo de escribir la primera vez | Guarda sólo `{ id: true }`; si guardas structs completos, un nodo renombrado rompe el save entero |
| Multiplicar un stat en `nodo_efecto_aplicar()` y sumarlo en `revertir()` (o viceversa) | Copiar-pegar entre las dos funciones sin revisar el operador | Escribe primero `aplicar()`, y genera `revertir()` invirtiendo el operador línea a línea, nunca a mano desde cero |
| Validar el árbol sólo visualmente, "se ve bien en el editor" | La validación por grafo parece trabajo extra para algo "obvio" | `arbol_validar()` (§3.2) cuesta un recorrido BFS; un ciclo o un huérfano en producción cuesta un ticket de soporte y una build de emergencia |
| Foco de UI sin sitio al abrir la pantalla del árbol | La primera vez que se abre, nadie ha pulsado nada todavía | Arranca `foco_id` en `raices[0]` (o en el último nodo comprado) en el Create de la pantalla, nunca en `undefined` |

---

## Ver también

- [13 · 01 — Diseño de juego: core loop, mecánicas, balance y dificultad](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) —
  gating con `global.progreso` (§5.3), curvas de dificultad (§3.2), la regla de sumideros (§4.3) y
  la telemetría (§9.5) que este documento extiende.
- [13 · 02 — Diseño de niveles](./02%20-%20Diseño%20de%20niveles.md) — *gating* duro, blando y de
  conocimiento (§1.4): el contraste que §3.6 usa para explicar por qué el árbol SÍ debe decir qué
  falta, al revés que el gating de mundo.
- [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md) — `repeticion_paso()`,
  `foco_rejilla()` (§2.2), `panel_dibujar()` (§3.4), `boton_nuevo()` y `pista_dibujar()` (§3.5),
  reutilizados sin reescribir en §3.6-§3.7.
- [13 · 10 — Testing y QA](./10%20-%20Testing%20y%20QA.md) — `scr_pruebas` (§3.1), el sitio natural
  para envolver `arbol_validar()` como prueba automática.
- [13 · 13 — Matemáticas aplicadas al juego](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
  las cinco curvas de crecimiento (§8) que este documento usa para el coste de nodos de rango
  (§1.4) sin repetir las fórmulas.
- [04 · 04 — RPG / Action RPG](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md) —
  `Stats`, `mods` y `Progression` (§5.0-§5.1): de donde salen los `skill_points` que este árbol
  gasta y el struct que `NodoEfecto.ESTADISTICA` modifica.
- [04 · 05 — Roguelike y generación procedural](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) —
  `RunState` y `MetaProgress` (§5.8): el patrón de monedas múltiples que §2.6 nombra y extiende.
- [04 · 06 — Metroidvania](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) — el
  gating por habilidades del mundo (que no debe pisarse con el árbol, §2.2) y el New Game+ por
  multiplicadores (§8, punto 8) que §2.3 reutiliza para el jugador que ya lo desbloqueó todo.
- [04 · 18 — Menús con scroll y navegación](../04%20-%20Recetas%20por%20género/18%20-%20Menús%20con%20scroll%20y%20navegación.md) —
  la idea de cámara/scroll que §3.7 traslada de una lista 1D a un grafo 2D.
- [04 · 32 — Sistema de daño y efectos de estado](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  `armadura`, `resistencias`, `dano_tipo_a_clave()` y `DanoTipo`: el pipeline al que §3.4 engancha
  los efectos de nodo, sin reescribirlo.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) —
  el sandbox, la regla de resolución y el sistema de guardado versionado que §3.5 envuelve.
- [`06 - Assets y Scripts/scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) —
  `save_game()`/`load_game()` y el hook `global.save_migrar`, usados tal cual en §3.5.

---

## Fuentes

Todas consultadas el **2026-09-06**.

**Diseño de fuera de GameMaker**

- **Passive Skill Tree**, página oficial de *Path of Exile* (Grinding Gear Games) —
  <https://www.pathofexile.com/passive-skill-tree> — «a vast web of 1325 skills», la definición
  textual de *Notable* y **Keystone** («fundamentally change the way you play, typically with one
  positive and one negative effect») y la mención de puntos de reinicio obtenidos por misión o por
  objeto raro. Es la fuente central de §1.1, §1.2 y §1.5.
- **Final Fantasy X**, Wikipedia (en inglés) — <https://en.wikipedia.org/wiki/Final_Fantasy_X> —
  la descripción del Sphere Grid como «a grid of interconnected nodes» y de la variante «Expert
  Sphere Grid» donde todos los personajes arrancan en el nodo central. Fuente de la fila de
  tablero/rejilla y de constelación/hub radial en §1.1.
- **Hades (video game)**, Wikipedia (en inglés) —
  <https://en.wikipedia.org/wiki/Hades_(video_game)> — la distinción entre Obolos y otros
  desbloqueos que se pierden al morir frente a la moneda que compra mejoras permanentes en la
  Casa, y el **Pact of Punishment** como sistema de dificultad opcional que el jugador activa a
  cambio de mejores recompensas. Fuente de §2.5 y de la fila de moneda de meta en §2.6.
- **Dead Cells**, Wikipedia (en inglés) — <https://en.wikipedia.org/wiki/Dead_Cells> — las Cells
  como moneda que compra mejoras permanentes y que se pierde entera si el jugador muere antes de
  gastarla. Fuente de la fila de Dead Cells en §2.6.
- ⚠️ La estructura de tres columnas por clase de *Diablo II* (§1.1) y los perks sin conexión de
  *Call of Duty* (§1.1) se citan de memoria, como ejemplos ilustrativos de una topología ya
  definida por la fuente primaria de esa fila: no se abrió ninguna fuente concreta sobre ellos
  esta sesión.
- ⚠️ La política de respec «nulo o casi nulo» de la última fila de §1.5 y el ejemplo de moneda de
  prestigio de §2.6 describen un patrón habitual del género, sin una fuente concreta abierta
  verificando un juego con nombre.
- La **curva exponencial con razón baja** para nodos de rango (§1.4), la **regla de sumideros**
  (§2.3) y el **método de simulación con `scr_pruebas`** (§1.6) remiten a
  [13 · 01](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
  y [13 · 13](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md), documentos ya verificados contra
  sus propias fuentes: no se repiten esas citas aquí.

**GameMaker (fuentes primarias)**

Todos los símbolos de GML de este documento se comprobaron con
`python3 "_indice/buscar.py" <símbolo>` contra el `GmlSpec.xml` del runtime **2026.0.0.23**:
familias *Variable Functions* (`variable_struct_exists`, `struct_get_names`, `array_push`,
`array_length`, `array_delete`, `array_find_index`, `is_undefined`), *File Handling*
(`buffer_load`, `buffer_read`, `buffer_string`, `buffer_delete`, `json_parse`, `file_exists`),
*Maths And Numbers* (`point_direction`, `angle_difference`), *Game Input*
(`keyboard_check`, `gamepad_button_check`, `gamepad_axis_value`, `gp_padu/padd/padl/padr`,
`gp_axislh/axislv`, `gp_face1`), *Drawing* (`draw_line_width`, `draw_rectangle`, `draw_set_color`)
y `struct_remove` (familia *Variable Functions*, usado en §3.3 y §3.5 para borrar un id de
`comprados`).

> ⚠️ **Lo que NO está verificado en este documento.** El código no se ha compilado en un proyecto
> real: los sprites (`spr_panel_nodo`) son marcadores de posición que hay que crear, igual que en
> el resto de la biblioteca. Los números de ejemplo —cobertura del 60-75 %, cono de 100° en la
> navegación, proporción de 3-5 nodos de relleno por Keystone— son puntos de partida razonables,
> no medidas de ningún juego concreto: ajústalos con telemetría real (§3.8) antes de tratarlos como
> regla fija.
