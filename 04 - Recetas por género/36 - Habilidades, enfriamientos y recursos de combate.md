# 36 · Habilidades, enfriamientos y recursos de combate

> Cómo se diseña y se programa una **habilidad activa**: la que el jugador (o un enemigo)
> decide lanzar en un instante concreto, paga por ella y espera para volver a usarla. Cubre el
> struct de habilidad dirigido por datos (coste, enfriamiento, cargas, tiempo de casteo,
> interrupción, objetivo válido), el gestor por entidad con enfriamiento global, los recursos
> de combate que la pagan —estamina, maná, furia— como una economía en miniatura, y la barra
> de acción que los enseña con un barrido radial y un contador de cargas.
>
> **Lo que NO cubre este documento** (y dónde está, para no repetirlo):
> - El **árbol de habilidades** —nodos, prerrequisitos, puntos, *respec*, la pantalla
>   navegable— es de
>   [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md).
>   Este documento es la habilidad **en sí** —cómo se ejecuta, cuánto cuesta, cuánto tarda en
>   volver a estar lista—, no cómo se desbloquea ni en qué orden. §3.8 muestra el único punto
>   de contacto entre ambos: comprobar el flag que el árbol ya escribe.
> - Las **habilidades-llave** de Metroidvania (doble salto, dash, agarre) de
>   [04 · 06 §4.2](./06%20-%20Metroidvania.md#42-habilidades-desbloqueables) son otra cosa por
>   completo: una llave permanente que abre una puerta del mapa, sin coste ni enfriamiento.
>   §1.1 traza la frontera exacta.
> - El **pipeline de daño** —tipos, resistencias, armadura, escudos, efectos de estado— es de
>   [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md).
>   Aquí sólo se **engancha** (§3.7): una habilidad que hace daño llama a `recibir_golpe()`,
>   no reescribe cómo se calcula.
> - La **economía general** (fuentes, sumideros, realimentación, cómo detectar inflación) es
>   de [13 · 01 §4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#4--economía-y-balance);
>   aquí se **aplica** ese vocabulario a estamina, maná y furia, sin repetirlo.
> - Los **componentes de UI genéricos** (botón, panel, `ancla()`, `aproximar()`) son de
>   [13 · 05 §3.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#35-los-componentes-clásicos);
>   la barra de acción de §3.9 se construye **sobre** ellos, no los redefine.
>
> **Hueco detectado:** la biblioteca ya tenía frame data de ataques (04 · 30), tipos de daño
> (04 · 32) y el grafo de progresión (13 · 16), pero ningún documento cerraba la pieza que
> conecta las tres: la habilidad como **dato con coste y tiempo**, el gestor que decide si se
> puede lanzar ahora mismo, y los recursos que la limitan. `estamina` no existía en ningún
> documento de la biblioteca antes de este (`grep -r "estamina"` → 0 resultados fuera de una
> mención de paso en 04 · 32 §1.7); `mp`/`mp_max` existían en 04 · 04 §5.0 sin que nada los
> gastara ni los mostrara.

---

## 1 · Los principios

### 1.1 Tres cosas que se llaman «habilidad» — y no son la misma

La palabra «habilidad» aparece en tres sistemas distintos de esta biblioteca, y confundirlos
es la forma más rápida de acabar con tres implementaciones que se pisan:

| | **Habilidad activa** (este documento) | **Habilidad-llave** ([04 · 06 §4.2](./06%20-%20Metroidvania.md#42-habilidades-desbloqueables)) | **Nodo del árbol** ([13 · 16](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md)) |
|---|---|---|---|
| Qué es | Una **acción** que el jugador decide ejecutar en un instante | Una **flag permanente** que cambia el conjunto de movimientos | Un **nodo de un grafo** que se compra con puntos |
| Coste | Recurso de combate (maná, estamina, furia) que se gasta y se regenera | Ninguno: una vez se tiene, se tiene siempre | Puntos de habilidad, una vez, al comprarlo |
| Se «gasta»? | Sí, cada vez que se usa | No | No: es una compra, no una acción |
| Tiempo de espera | Enfriamiento en fotogramas (§1.3) | No aplica | No aplica |
| Ejemplo | Bola de fuego, curación, esquiva con recurso, grito de furia | Doble salto, dash, agarre de pared | «+8 % de armadura», «tu esquive atraviesa enemigos» |
| Cómo se guarda | `GestorHabilidades` por entidad (§3.3): enfriamientos y cargas actuales | `global.world.flags[$ "doble_salto"]` (04 · 06 §4.4) | `comprados` en el grafo (13 · 16 §3.1) |

**El punto de contacto real entre los tres**, y el único que este documento toca, es que una
habilidad activa puede necesitar estar **desbloqueada** por el árbol antes de poder lanzarse:
eso es un `NodoEfecto.HABILIDAD` de 13 · 16 §3.4 escribiendo un flag en `global.progreso`, y
`GestorHabilidades` leyéndolo antes de permitir el lanzamiento (§3.8). Ni el árbol conoce el
enfriamiento de la habilidad, ni el gestor conoce cómo se compró: cada uno hace una cosa.

### 1.2 Los seis campos que convierten una habilidad en un dato

Igual que un ataque cuerpo a cuerpo es un struct en `global.ataques` y no una rama de código
([04 · 30 §2.3](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#23-los-datos-un-struct-por-ataque)),
una habilidad activa es un struct en `global.habilidades`. El encargo de este documento fija
seis campos mínimos; el resto son variaciones sobre ellos:

| Campo | Qué resuelve | Pregunta que responde |
|---|---|---|
| **Coste** | Cuánto recurso consume | «¿Puedo permitírmela ahora mismo?» |
| **Enfriamiento** | Fotogramas hasta poder volver a lanzarla | «¿Cuánto tengo que esperar tras usarla?» |
| **Cargas** | Cuántas veces se puede lanzar de golpe antes de esperar | «¿Es "lista/no lista" o tengo un stock?» |
| **Tiempo de casteo** | Fotogramas entre pulsar el botón y que el efecto ocurra | «¿Es instantánea o tengo que exponerme un rato?» |
| **Interrupción** | Si un golpe recibido durante el casteo lo cancela | «¿Me pueden cortar la jugada?» |
| **Objetivo válido** | Sobre quién o dónde se resuelve el efecto | «¿A quién le toca, y cómo se elige?» |

Ninguno de los seis es opcional en el struct (aunque su valor pueda ser «cero» o «ninguno»):
una habilidad instantánea, sin coste, ilimitada, sigue teniendo los seis campos — sólo que
`coste: 0`, `casteo: 0`, `cargas_max: infinity` los anulan sin necesitar un camino de código
distinto. Es el mismo principio que 04 · 30 aplica a `rebote` o `rompe_bloqueo`: campos que
casi siempre son el valor neutro, y que cuando no lo son cambian una habilidad concreta sin
tocar el gestor.

### 1.3 Enfriamiento por habilidad y enfriamiento global: qué evita cada uno

Son dos temporizadores con trabajos distintos, y un error habitual es implementar sólo uno:

- **El enfriamiento por habilidad** evita que *esa* habilidad se repita sin parar. Sin él, una
  bola de fuego con coste 1 de maná y un jugador con 99 de maná es una ametralladora.
- **El enfriamiento global** (GCD, *global cooldown*) evita que el jugador encadene **varias
  habilidades distintas** en el mismo fotograma para sacar todo su daño de golpe sin ningún
  ritmo entre acciones. Sin él, un jugador con cinco habilidades sin enfriamiento propio las
  lanza las cinco en el mismo instante.

No todos los géneros necesitan las dos piezas. La wiki oficial de *League of Legends* describe
el diseño de *cooldown* del juego como **puramente por habilidad**, sin ningún temporizador
compartido: *"the amount of time before a champion ability, item, summoner spell or rune can
be used again after activation"* es la única definición de *cooldown* que da la página, y su
lista de tipos —normal, estático, por objetivo, con cargas— no incluye ningún mecanismo
global (<https://wiki.leagueoflegends.com/en-us/Cooldown>, consultado 2026-09-06: *"the
document makes no mention of a global cooldown mechanic affecting all abilities uniformly"*).
Eso tiene sentido para un MOBA de acción continua, donde el ritmo lo pone el jugador moviendo
el ratón, no un temporizador compartido. Un RPG por turnos o un MMO con una barra de
habilidades larga sí suele necesitarlo: sin él, la decisión deja de ser «¿qué lanzo ahora?» y
pasa a ser «¿en qué orden vacío la barra en el mismo segundo?».

**La regla práctica:** si tu combate tiene **movimiento libre y apuntado activo** (twin-stick,
Action RPG en tiempo real), casi nunca hace falta GCD — el propio movimiento ya impone ritmo.
Si tiene **una barra de más de tres o cuatro habilidades sin coste de posicionamiento** (RPG
por turnos con ATB, MMO de barra larga), el GCD es casi obligatorio. `GestorHabilidades`
(§3.3) implementa ambos, pero cada `HabilidadDef` decide con `usa_gcd: bool` si le afecta —
así una habilidad instantánea de bajo impacto (un parpadeo defensivo) puede quedar fuera del
GCD sin tener que desactivarlo para toda la barra.

> ⚠️ El valor concreto del GCD en juegos de referencia (1,5 s es la cifra que circula para
> varios MMO) se cita de memoria: no se ha verificado ninguna fuente primaria esta sesión.
> Trátalo como punto de partida, no como número canónico — ajústalo jugando (§2.3).

### 1.4 Cargas: cuando «lista/no lista» no basta

Un enfriamiento por habilidad modela una habilidad que está **lista** o **no lista**. Un
sistema de cargas modela algo distinto: un **stock** de N usos que se recarga uno a uno,
independientemente de si ya se ha gastado alguno. La propia wiki de *League of Legends* lo
define así: *"An effect with a recharge will cost a charge to cast. The effect stores multiple
charges up to a maximum, and generates one after the recharge is complete"*
(<https://wiki.leagueoflegends.com/en-us/Cooldown>, consultado 2026-09-06), con dos ejemplos
numéricos reales de la misma página:

| Habilidad | Enfriamiento por carga (por nivel) | Cargas máximas | Cita |
|---|---|---|---|
| *Bandage Toss* (Amumu) | 16 / 15 / 14 / 13 / 12 s | 2 | «Amumu periodically stocks a charge of Bandage Toss, up to 2» |
| *Yordle Snap Trap* (Caitlyn) | 26 / 22 / 18 / 14 / 10 s | hasta un tope | «Caitlyn periodically stocks a charge of Yordle Snap Trap, up to a cap» |

El detalle que la propia fuente no aclara —y que hay que fijar tú mismo, porque es una
decisión de diseño, no un hecho objetivo— es si el temporizador de recarga corre **en
paralelo** para cada carga que falta o **uno detrás de otro**. La implementación de §3.3 usa
un único temporizador secuencial (recarga la carga que falta, y sólo cuando termina empieza a
contar la siguiente): es la lectura más simple de «periodically stocks», es la que usan la
mayoría de sistemas de cargas de referencia, y es la que evita que rellenar el stock entero
sea instantáneo si has dejado pasar mucho tiempo sin gastar ninguna.

**Cuándo usar cargas en vez de un enfriamiento simple:** cuando quieres premiar al jugador que
guarda el recurso para un momento crítico (dos esquivas con recurso seguidas para atravesar un
patrón) sin que eso signifique que la habilidad no tiene límite. `cargas_max: 1` es,
matemáticamente, el caso particular sin cargas: por eso §3.1 no separa dos structs distintos.

### 1.5 Un recurso de combate es una economía en miniatura

Estamina, maná y furia no son «una barra que baja y sube»: son la misma pieza de vocabulario
que [13 · 01 §4.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto)
ya define para la economía general del juego, aplicada a una escala de segundos en vez de
minutos:

| Pieza (13 · 01 §4.1) | En un recurso de combate |
|---|---|
| **Pool** | La estamina, el maná o la furia actuales de una entidad |
| **Fuente** | El paso del tiempo (regeneración pasiva) o golpear (furia) |
| **Sumidero** | Esquivar, castear, o gastar la furia en un golpe cargado |
| **Realimentación** | Positiva si golpear da más furia para golpear más fuerte (§1.6); se acota con un techo y con el sumidero del gasto |

Y la regla de 13 · 01 §4.3 se aplica sin cambiar una palabra: **todo recurso de combate
necesita un sumidero**, o dejará de significar nada. Un maná que sólo se regenera y nunca se
gasta (porque el jugador no encuentra la habilidad rentable) es un número muerto en la HUD; una
furia sin techo ni decaimiento se vuelve un contador que sólo sube y dejas de mirar. §3.2
resuelve el sumidero de la furia con **decaimiento fuera de combate** — la propia furia se
autolimita si no se usa, sin que haga falta una regla de diseño aparte.

### 1.6 Tres arquetipos de recurso, y cuándo usar cada uno

La wiki oficial de *League of Legends* documenta más de una docena de recursos distintos entre
sus campeones, pero todos caen en tres familias con una regla de diseño clara detrás de cada
una (<https://wiki.leagueoflegends.com/en-us/Ability_resource>, consultado 2026-09-06):

| Arquetipo | Cómo se genera | Cómo se limita | Cita textual | Ejemplo en este documento |
|---|---|---|---|---|
| **Regenerativo lento** (maná) | Pasivamente, con el tiempo | Regeneración «low» y «limited pool»: el límite es la cantidad, no la velocidad | *"expended through abilities... regeneration low, limited pool"* | `mana`, §3.2 |
| **Regenerativo rápido con techo bajo** (energía/estamina) | Pasivamente, deprisa | La regeneración es alta pero el máximo no se puede ampliar mucho: «casting too many abilities... will deplete it quickly, leaving the user unable to cast again for a short period» | *"much higher [regen] than mana but pool cannot be improved"* | `estamina`, §3.2 |
| **Ganado por acción, con decaimiento** (furia) | Por combatir, no por esperar: *"must be generated first in order to be usable"* | Decae si dejas de generarlo: *"may or may not decay when out-of-combat"*; su propósito declarado es *"represents momentum and encourages sustained aggression"* | *"encourages sustained aggression"* | `furia`, §3.2 |

Esto responde directamente a I2 de la auditoría: **estamina y maná no son el mismo arquetipo**
aunque ambos «se regeneren solos» — la diferencia de diseño está en la velocidad de
regeneración frente al tamaño del pool, no en si regeneran. Y **furia no es un tercer maná**:
es un recurso que castiga la pasividad en vez de premiar la paciencia, lo contrario de maná.
Elige el arquetipo por lo que quieres que el jugador *sienta al no usarlo*: con maná, esperar
es gratis; con estamina, esperar es lo normal entre acciones; con furia, esperar es perder lo
que ya tenías.

### 1.7 Casteo, canalización e interrupción: frame data para lo que no es un golpe

Una habilidad con `casteo > 0` tiene la misma estructura de tres fases que un ataque cuerpo a
cuerpo — arranque, ventana activa, recuperación ([04 · 30 §1.2](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#12-el-vocabulario-mínimo-frame-data)) —
sólo que la «ventana activa» no es una hitbox sino el instante en que se resuelve el efecto.
Por eso una habilidad canalizada **te expone exactamente igual que un ataque lento**: el
jugador rival lo sabe y lo castiga igual.

El artículo de Wikipedia sobre el género *Soulslike* describe esa exposición como parte
central del combate «metódico» del género: *"Combat in Soulslike games may also be methodical,
requiring the player to monitor stamina to avoid overexertion of their character"*, y
relaciona explícitamente esa gestión de estamina con la imposibilidad de cancelar animaciones
a mitad: el sistema que la wiki llama *"animation priority"*, donde *"players cannot cancel
animations until completion"* (<https://en.wikipedia.org/wiki/Soulslike>, consultado
2026-09-06). Esa es exactamente la razón de ser del campo `interrumpible` de §1.2: una
habilidad sin armadura de casteo (`interrumpible: true`) puede cortarse a mitad de canalización
si te golpean — el coste ya pagado se pierde, y esa pérdida es la que hace que castear en
mitad de un combate sea una decisión, no un trámite. Una habilidad con armadura
(`interrumpible: false`, el equivalente al *super armor* de 04 · 30 §4.7) sigue adelante pase
lo que pase: resérvala para pocas habilidades, o el aturdimiento deja de significar nada.

---

## 2 · El método, paso a paso

### 2.1 La ficha de habilidad, antes de programar nada

Rellena esta tabla para cada habilidad **antes** de tocar `global.habilidades`. Si no sabes
qué poner en una columna, todavía no sabes qué hace la habilidad.

| Campo | Bola de fuego | Curación | Esquiva con recurso | Grito de furia (definitiva) |
|---|---|---|---|---|
| Recurso | Maná | Maná | Estamina | Furia |
| Coste | 15 | 25 | 20 | 50 (mínimo; gasta toda la disponible, §3.7) |
| Enfriamiento | 90 F (1,5 s) | 300 F (5 s) | 0 (sólo lo limita el recurso) | 600 F (10 s) |
| Cargas máx. | 1 | 1 | 2 | 1 |
| Casteo | 24 F (0,4 s) | 36 F (0,6 s) | 0 (instantánea) | 12 F (0,2 s) |
| Interrumpible | Sí | Sí | No aplica (0 casteo) | No (armadura) |
| Objetivo | Enemigo en cono | Uno mismo | Uno mismo (dirección de movimiento) | Área alrededor |
| Usa GCD | Sí | Sí | No | Sí |
| Qué hace legible | El brillo del icono cuando hay maná de sobra para lanzarla dos veces | El bloqueo de curación en combate (04 · 32 §5.9) si se intenta en mal momento | El barrido radial vacío del icono cuando no queda estamina | La barra de furia llena, con pulso, antes de poder lanzarla |

La última fila importa tanto como las demás: una habilidad que el jugador no entiende sin leer
un tooltip está mal comunicada, no mal diseñada. §3.9 traduce cada fila en un elemento visual
concreto de la barra de acción.

### 2.2 Elegir el recurso según el arquetipo de combate

| Tu combate se parece a… | Recurso principal | Por qué |
|---|---|---|
| Acción con esquiva y i-frames (Souls-like, 04 · 30 §4.5) | Estamina | Limita esquivar Y atacar con el MISMO recurso: fuerza elegir entre defender y golpear |
| Lanzador de hechizos con posicionamiento (Action RPG, 04 · 04) | Maná | Permite planificar varios turnos por adelantado; la escasez es lenta, no inmediata |
| Berserker cuerpo a cuerpo agresivo | Furia | Premia entrar en el rango de golpeo en vez de mantener las distancias; decae si te quedas quieto (§1.6) |
| Shooter con habilidades de apoyo | Munición o cargas puras, sin regeneración pasiva (fuera de alcance: ver [04 · 34](./34%20-%20Combate%20a%20distancia%20-%20armas,%20munición%20y%20balística.md) para munición de armas) | El recurso se repone por recogida, no por espera: cambia el ritmo entero |

No hace falta un único recurso por juego: un Action RPG con maná para hechizos y estamina para
esquivar (como en la ficha de §2.1) es la combinación más común, precisamente porque cada una
limita una **familia de acciones** distinta.

### 2.3 Balancear coste y enfriamiento juntos: el DPS efectivo

Balancear el coste sin mirar el enfriamiento (o al revés) es el error que hace que una
habilidad «barata» resulte inútil porque tarda demasiado en volver, o que una habilidad
«fuerte» resulte rota porque se puede repetir sin parar. La métrica que los junta es la misma
familia que el TTK de
[13 · 01 §4.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#44--balance-por-fórmulas-con-números):

```
  ciclo_total (F)     = enfriamiento + casteo
  dano_por_ciclo       = dano_del_efecto
  dps_efectivo         = dano_por_ciclo / (ciclo_total / 60)     // daño por segundo, sostenido
```

Con la bola de fuego de §2.1 (`dano: 22`, `enfriamiento: 90`, `casteo: 24`):

```
  ciclo_total = 90 + 24 = 114 F = 1,9 s
  dps_efectivo = 22 / 1,9 ≈ 11,6
```

Compárala contra el golpe ligero cuerpo a cuerpo de 04 · 30 §5.1 (`dano: 6`, arranque 4 +
activo 3 + recuperación 9 = 16 F por golpe, encadenable): `dps ≈ 6 / (16/60) = 22,5`. La bola
de fuego hace menos DPS sostenido que la cadena ligera — es correcto **si** su ventaja es otra
cosa (alcance, no exponerse cuerpo a cuerpo, un tipo de daño que atraviesa una resistencia
concreta). Si no tiene ninguna ventaja compensatoria y aun así hace menos DPS, no hay razón
para elegirla nunca: **el coste del recurso es la tercera variable** que debe justificar la
diferencia — gastar maná por menos DPS sólo tiene sentido si el maná es abundante o si el
alcance evita daño que sí recibirías cuerpo a cuerpo.

**Regla práctica:** fija el `dano_por_ciclo` con la unidad de golpe estándar de 13 · 01 §4.4
(«esta habilidad vale 3,7 golpes estándar»), y ajusta el `enfriamiento` y el `casteo` para que
el `dps_efectivo` caiga donde quieres respecto al DPS del arma básica — nunca al revés
(ajustar el daño a un enfriamiento arbitrario es como fijar el precio antes de saber qué
compra).

### 2.4 Cuándo NO hace falta este sistema

- **Un solo botón de acción sin variantes** (saltar, disparar siempre la misma bala): eso es
  una mecánica base, no una habilidad — no le pongas un `HabilidadDef` a algo que no tiene
  coste ni elección. Ver [04 · 01 — Plataformas 2D](./01%20-%20Plataformas%202D.md) y
  [04 · 11 — Arcade y juegos de un botón](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md).
- **Un roguelike de disparos con un único arma activa por vez** que sólo cambia al recoger otra
  (sin cargador de habilidades): la munición de esa arma es de
  [04 · 34](./34%20-%20Combate%20a%20distancia%20-%20armas,%20munición%20y%20balística.md), no
  de este documento.
- **Un juego de un solo personaje sin sistema de progresión**: si nunca vas a tener más de una
  o dos acciones especiales fijas, un `alarm` y una variable de instancia bastan; el gestor de
  §3.3 sólo paga su complejidad cuando hay tres o más habilidades compitiendo por los mismos
  recursos y el mismo GCD.

---

## 3 · Cómo se traduce a GameMaker

### 3.0 Dónde vive cada cosa

| Struct / función | Responsabilidad | Sección |
|---|---|---|
| `global.habilidades` | Datos de cada habilidad: coste, enfriamiento, cargas, casteo, interrupción, objetivo, efecto | §3.1 |
| `RecursoCombate` | Un pool con fuente, sumidero y retardo — estamina, maná o furia según los parámetros | §3.2 |
| `GestorHabilidades` | Enfriamientos, enfriamiento global, cargas y el casteo en curso — uno por entidad | §3.3 |
| `recibir_golpe()` (04 · 30 §5.7, extendido en 04 · 32 §5.7) | Aplica el daño de una habilidad ofensiva — no se reescribe, se llama | §3.7 |
| `combate.efectos` (04 · 32 §5.4) | Aplica estados (veneno, aturdimiento) que una habilidad conceda | §3.7 |
| `global.progreso` (13 · 16 §3.4) | Flags de desbloqueo que `GestorHabilidades` consulta antes de lanzar | §3.8 |
| Slot de la barra de acción | Icono, barrido radial de enfriamiento, contador de cargas — uno por habilidad visible | §3.9 |

### 3.1 El struct de habilidad dirigido por datos

```gml
// ---------------------------------------------------------------------------
// scr_habilidades_config
// Verificado: ninguno de estos símbolos es del runtime — son macros propias.
// ---------------------------------------------------------------------------

#macro ENFRIAMIENTO_GLOBAL_FRAMES  36   // 0,6 s a 60 fps — §1.3. 0 = sin GCD.

// A qué o a quién se aplica el efecto de una habilidad.
enum ObjetivoHabilidad
{
    UNO_MISMO,             // el propio lanzador (curación, buff, esquiva con recurso)
    ENEMIGO_MAS_CERCANO,   // sin cono: el más cercano de un objeto/padre dado
    ENEMIGO_EN_CONO,       // el más cercano dentro de un ángulo frente al lanzador
    AREA_EN_PUNTO          // no hay instancia objetivo: el efecto recibe un punto (x, y)
}
```

```gml
// ---------------------------------------------------------------------------
// scr_habilidades — datos. Se ejecuta una vez al arrancar el juego, igual que
// global.ataques en 04 · 30 §5.1: es el mismo patrón de "struct por entrada",
// aplicado a habilidades en vez de a golpes cuerpo a cuerpo.
//
// LOS SEIS CAMPOS DEL ENCARGO (§1.2), en cada entrada:
//   coste, enfriamiento, cargas_max, casteo, interrumpible, objetivo.
// Todo lo demás (icono, alcance, cono_grados, flag_requerido, efecto) es
// variación sobre ellos, no un séptimo concepto.
// ---------------------------------------------------------------------------
global.habilidades =
{
    bola_fuego : {
        nombre        : "Bola de fuego",
        icono         : spr_icono_bola_fuego,          // marcador de posición
        sonido        : snd_bola_fuego,                 // marcador de posición
        recurso       : "mana",
        coste         : 15,
        enfriamiento  : 90,          // 1,5 s
        cargas_max    : 1,
        casteo        : 24,          // 0,4 s de canalización antes de resolverse
        interrumpible : true,
        usa_gcd       : true,
        objetivo      : ObjetivoHabilidad.ENEMIGO_EN_CONO,
        objeto_objetivo : obj_enemigo,                  // padre de las instancias válidas
        alcance       : 220,
        cono_grados   : 50,
        flag_requerido : "",         // "" = no depende del árbol de 13 · 16 (ver §3.8)
        efecto : function(_lanzador, _objetivo, _punto)
        {
            habilidad_efecto_bola_fuego(_lanzador, _objetivo);   // §3.7
        }
    },

    curacion : {
        nombre        : "Curación",
        icono         : spr_icono_curacion,
        sonido        : snd_curacion,
        recurso       : "mana",
        coste         : 25,
        enfriamiento  : 300,         // 5 s: cura de más en más tiempo es un sumidero de tiempo
        cargas_max    : 1,
        casteo        : 36,          // 0,6 s: te expones para curarte, no es gratis
        interrumpible : true,
        usa_gcd       : true,
        objetivo      : ObjetivoHabilidad.UNO_MISMO,
        objeto_objetivo : noone,
        alcance       : 0,
        cono_grados   : 0,
        flag_requerido : "",
        efecto : function(_lanzador, _objetivo, _punto)
        {
            habilidad_efecto_curacion(_lanzador);        // §3.7
        }
    },

    esquiva_estamina : {
        nombre        : "Esquiva",
        icono         : spr_icono_esquiva,
        sonido        : -1,
        recurso       : "estamina",
        coste         : 20,
        enfriamiento  : 0,           // sin enfriamiento propio: sólo lo limita la estamina
        cargas_max    : 2,           // dos esquivas seguidas antes de esperar
        cargas_recarga : 45,         // 0,75 s por carga (§1.4)
        casteo        : 0,           // instantánea: la propia FSM de 04 · 30 §5.8 la resuelve
        interrumpible : true,
        usa_gcd       : false,       // esquivar NUNCA debe bloquearse por el GCD de un hechizo
        objetivo      : ObjetivoHabilidad.UNO_MISMO,
        objeto_objetivo : noone,
        alcance       : 0,
        cono_grados   : 0,
        flag_requerido : "",
        efecto : function(_lanzador, _objetivo, _punto) { /* la resuelve la FSM, §3.6 */ }
    },

    grito_furia : {
        nombre        : "Grito de furia",
        icono         : spr_icono_furia_definitiva,
        sonido        : snd_furia_definitiva,
        recurso       : "furia",
        coste         : 50,          // MÍNIMO para lanzarla: el efecto gasta lo que haya (§3.7)
        enfriamiento  : 600,         // 10 s: una definitiva de verdad
        cargas_max    : 1,
        casteo        : 12,
        interrumpible : false,       // armadura de casteo (§1.7): es la recompensa de llegar a 100
        usa_gcd       : true,
        objetivo      : ObjetivoHabilidad.AREA_EN_PUNTO,
        objeto_objetivo : obj_enemigo,
        alcance       : 96,
        cono_grados   : 360,
        flag_requerido : "arbol_berserker_furia",   // 13 · 16 §3.4 — NodoEfecto.HABILIDAD
        efecto : function(_lanzador, _objetivo, _punto)
        {
            habilidad_efecto_grito_furia(_lanzador, _punto);   // §3.7
        }
    }
};
```

> 🔺 **Si una habilidad no tiene sistema de cargas (`cargas_max: 1`), no hace falta escribir
> `cargas_recarga`.** `GestorHabilidades.registrar()` (§3.3) usa `enfriamiento` como recarga de
> la única carga cuando `cargas_recarga` no está definido — así una habilidad simple no
> necesita rellenar un campo que para ella no significa nada distinto del enfriamiento.

### 3.2 `RecursoCombate`: el pool genérico, y sus tres variantes

El struct reutiliza el mismo patrón retardo/espera/regeneración que ya tienes en `Escudo`
([04 · 32 §5.3](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#53-escudos)):
gastar reinicia una espera, y sólo cuando la espera llega a cero el pool se mueve hacia su
fuente. La única generalización es que `regen_por_frame` puede ser **negativo** — eso es lo
que convierte el mismo struct en un recurso que decae en vez de regenerar, sin un segundo
sistema para la furia:

```gml
// ---------------------------------------------------------------------------
// scr_recurso_combate
// Verificado: clamp, max, min
// ---------------------------------------------------------------------------

/// @func RecursoCombate(_maximo, _regen_por_frame, _retardo_frames)
/// @desc Un pool con fuente, sumidero y retardo (13 · 01 §4.1, §1.5 de este
///       documento). El SIGNO de `_regen_por_frame` decide el arquetipo:
///         positivo → regenera solo  (estamina, maná, §1.6)
///         negativo → decae solo     (furia, §1.6)
///         cero     → no cambia solo (un recurso puramente "ganado", munición)
/// @param {Real} _maximo
/// @param {Real} _regen_por_frame  Unidades por fotograma. Puede ser negativo.
/// @param {Real} _retardo_frames   Fotogramas de gracia tras gastar/ganar antes
///                                 de que el regen/decaimiento vuelva a correr.
function RecursoCombate(_maximo, _regen_por_frame, _retardo_frames) constructor
{
    actual           = _maximo;
    maximo           = _maximo;
    regen_por_frame  = _regen_por_frame;
    retardo_frames   = _retardo_frames;
    espera           = 0;

    /// @desc ¿Hay suficiente para pagar _cantidad? No gasta nada.
    static hay_suficiente = function(_cantidad)
    {
        return actual >= _cantidad;
    };

    /// @desc SUMIDERO (13 · 01 §4.1). Gastar reinicia el retardo: tras esquivar,
    ///       la estamina no empieza a subir hasta pasado `retardo_frames`.
    static gastar = function(_cantidad)
    {
        actual  = max(0, actual - _cantidad);
        espera  = retardo_frames;
    };

    /// @desc FUENTE activa (13 · 01 §4.1): furia al golpear, una poción de maná.
    ///       También reinicia el retardo — para la furia, esto es lo que le da
    ///       el "grace period" fuera de combate antes de empezar a decaer.
    static ganar = function(_cantidad)
    {
        actual  = min(maximo, actual + _cantidad);
        espera  = retardo_frames;
    };

    /// @desc Un tic por fotograma. Llámalo desde GestorHabilidades.tick() (§3.3)
    ///       o desde el Step de la entidad si no usas habilidades para gastarlo.
    static tick = function()
    {
        if (espera > 0) { espera--; return; }
        if (regen_por_frame != 0)
        {
            actual = clamp(actual + regen_por_frame, 0, maximo);
        }
    };
}
```

Las tres variantes de la ficha de §2.1, con los números derivados de la tabla de arquetipos de
§1.6 (regen alto y techo bajo para estamina; regen bajo para maná; decaimiento con gracia larga
para furia):

```gml
// obj_jugador — Create
recursos = {
    estamina : new RecursoCombate(100, 0.55, 45),   // ~3 s de 0 a 100; 0,75 s de gracia
    mana     : new RecursoCombate(50,  0.10, 0),     // lento, SIN penalización por gastar
    furia    : new RecursoCombate(100, -0.20, 180)   // decae; 3 s de gracia tras el último golpe
};
```

> 💡 **Si tu proyecto ya usa el `Stats` de [04 · 04 §5.0](./04%20-%20RPG%20_%20Action%20RPG.md#50-estadísticas)**
> (que declara `mp`/`mp_max` sin que nada los gaste todavía — el hueco exacto que detectó la
> auditoría), no crees un segundo maná: sincroniza `RecursoCombate` con esos campos en vez de
> con los suyos propios.
> ```gml
> recursos.mana = new RecursoCombate(stats.mp_max, 0.10, 0);
> recursos.mana.actual = stats.mp;                 // arranca igualado
> // ... tras cualquier cambio (gastar/ganar/tick): stats.mp = recursos.mana.actual;
> ```
> Es una sincronización de una línea, no una abstracción nueva: sigue habiendo un único sitio
> donde vive el maná de verdad (`stats.mp`), `RecursoCombate` sólo le presta la lógica de
> gasto/regeneración que `Stats` no tenía.

### 3.3 `GestorHabilidades`: enfriamientos, enfriamiento global y cargas, por entidad

```gml
// ---------------------------------------------------------------------------
// scr_gestor_habilidades
// Verificado: array_push, array_length, variable_struct_exists, is_callable,
//             instance_exists, variable_instance_exists
// ---------------------------------------------------------------------------

/// @func GestorHabilidades(_recursos)
/// @param {Struct} _recursos  El struct { estamina, mana, furia, ... } de §3.2.
function GestorHabilidades(_recursos) constructor
{
    recursos        = _recursos;
    claves          = [];    // orden de registro — evita enumerar el struct cada frame
    enfriamiento    = {};    // clave → fotogramas restantes del enfriamiento PROPIO
    cargas          = {};    // clave → cargas disponibles ahora mismo
    carga_restante  = {};    // clave → fotogramas hasta la próxima carga (0 = a tope)
    enfriamiento_global = 0;
    casteo          = undefined;   // { clave, restante, total, lanzador, objetivo, punto }
    __recarga_de    = {};    // clave → fotogramas de recarga de UNA carga (pseudo-privado)

    /// @desc Da de alta una habilidad para esta entidad. Llámalo una vez por
    ///       habilidad que la entidad pueda lanzar, normalmente en el Create.
    static registrar = function(_clave)
    {
        var _def = global.habilidades[$ _clave];
        var _recarga_carga = variable_struct_exists(_def, "cargas_recarga")
                            ? _def.cargas_recarga : _def.enfriamiento;

        array_push(claves, _clave);
        enfriamiento[$ _clave]   = 0;
        cargas[$ _clave]         = _def.cargas_max;
        carga_restante[$ _clave] = 0;
        __recarga_de[$ _clave]   = _recarga_carga;    // guardado aparte: no se recalcula cada tick
    };

    /// @desc Un tic por fotograma. Llámalo junto a combate.tick() (04 · 30 §6).
    static tick = function()
    {
        if (enfriamiento_global > 0) enfriamiento_global--;

        for (var _i = 0; _i < array_length(claves); _i++)
        {
            var _clave = claves[_i];
            var _def   = global.habilidades[$ _clave];

            if (enfriamiento[$ _clave] > 0) enfriamiento[$ _clave]--;

            if (cargas[$ _clave] < _def.cargas_max)
            {
                carga_restante[$ _clave]--;
                if (carga_restante[$ _clave] <= 0)
                {
                    cargas[$ _clave]++;
                    // Un solo temporizador activo a la vez (§1.4): la carga N+1 no
                    // empieza a recargar hasta que la N ya ha terminado.
                    carga_restante[$ _clave] = (cargas[$ _clave] < _def.cargas_max)
                                              ? __recarga_de[$ _clave] : 0;
                }
            }
        }

        if (casteo != undefined) __tick_casteo();
    };

    /// @desc ¿Se puede lanzar AHORA MISMO? No gasta nada: es sólo la pregunta.
    static puede_lanzar = function(_clave)
    {
        if (casteo != undefined)                        return false;   // ya canalizando otra
        if (!habilidad_desbloqueada(_clave))             return false;  // §3.8
        var _def = global.habilidades[$ _clave];

        if (_def.usa_gcd && enfriamiento_global > 0)     return false;
        if (enfriamiento[$ _clave] > 0)                  return false;
        if (cargas[$ _clave] <= 0)                       return false;
        if (_def.recurso != ""
        &&  !recursos[$ _def.recurso].hay_suficiente(_def.coste))
                                                          return false;
        return true;
    };

    /// @desc Intenta lanzar. Gasta el recurso y consume una carga SIEMPRE que
    ///       puede_lanzar() ya haya dicho que sí — nunca antes.
    /// @returns {Bool}  true si el lanzamiento arrancó (instantáneo o casteo).
    static intentar_lanzar = function(_clave, _lanzador, _objetivo = noone, _punto = undefined)
    {
        if (!puede_lanzar(_clave)) return false;
        var _def = global.habilidades[$ _clave];

        if (_def.recurso != "") recursos[$ _def.recurso].gastar(_def.coste);   // §1.5, sumidero
        cargas[$ _clave]--;
        if (carga_restante[$ _clave] <= 0) carga_restante[$ _clave] = __recarga_de[$ _clave];

        if (_def.casteo <= 0)
        {
            __resolver(_clave, _lanzador, _objetivo, _punto);
        }
        else
        {
            casteo = { clave: _clave, restante: _def.casteo, total: _def.casteo,
                       lanzador: _lanzador, objetivo: _objetivo, punto: _punto };
        }
        return true;
    };

    /// @desc Avanza el casteo en curso un fotograma. Pseudo-privado (§ convención
    ///       de doble guion bajo, 13 · 23 §3 y `_INDICE-RECETAS.md`).
    static __tick_casteo = function()
    {
        var _def = global.habilidades[$ casteo.clave];

        // Sólo se corta si LA HABILIDAD lo permite (§1.7). El coste ya se
        // cobró: una interrupción es un riesgo asumido, no un "deshacer" gratis.
        if (_def.interrumpible
        &&  instance_exists(casteo.lanzador)
        &&  !casteo.lanzador.combate.tiene_control())
        {
            casteo = undefined;
            return;
        }

        casteo.restante--;
        if (casteo.restante <= 0)
        {
            __resolver(casteo.clave, casteo.lanzador, casteo.objetivo, casteo.punto);
            casteo = undefined;
        }
    };

    static __resolver = function(_clave, _lanzador, _objetivo, _punto)
    {
        var _def = global.habilidades[$ _clave];

        enfriamiento[$ _clave] = _def.enfriamiento;
        if (_def.usa_gcd) enfriamiento_global = ENFRIAMIENTO_GLOBAL_FRAMES;

        if (is_callable(_def.efecto)) _def.efecto(_lanzador, _objetivo, _punto);
    };
}
```

> 💡 **Cooldown reduction, si tu juego lo necesita.** La wiki de *League of Legends* fija la
> fórmula exacta de su estadística de *ability haste*: **"Cooldown Reduction =
> Haste/(100+Haste)"**, con un tope declarado de 500 de *haste* = 83,3 % de reducción
> (<https://wiki.leagueoflegends.com/en-us/Ability_haste>, consultado 2026-09-06). Si añades
> una estadística parecida, aplícala en `__resolver()` sobre `_def.enfriamiento`, NUNCA sobre
> `enfriamiento[$ _clave]` después de asignarlo — así una habilidad que ya recargando no
> cambia de duración a mitad si el jugador se equipa algo a mitad de partida. Márcalo como
> `reducible_por_haste: bool` en el `HabilidadDef` si sólo algunas habilidades deben verse
> afectadas (la propia wiki documenta *"Static Cooldowns"* que explícitamente no se reducen
> nunca — el mismo caso de uso).

### 3.4 El flujo completo de un intento de lanzamiento

```
  Input del jugador (botón de habilidad)
        │
        ▼
  puede_lanzar(clave)? ──NO──► feedback de "no disponible" (sonido de error,
        │                       parpadeo del icono — 13 · 05 §3.5 a) mismo patrón
        │ SÍ                    que un botón inactivo)
        ▼
  intentar_lanzar(): gasta el recurso, consume una carga
        │
        ├─ casteo == 0 ──────────► __resolver() YA MISMO
        │
        └─ casteo > 0 ───────────► arranca la canalización
                                          │
                                    cada tick(): ¿interrumpible Y sin control?
                                          │
                                    NO ───┴─── SÍ
                                    │           │
                              sigue contando   se cancela, SIN devolver el coste
                                    │
                              restante == 0
                                    │
                                    ▼
                              __resolver(): enfriamiento + GCD + efecto()
```

El coste se cobra en `intentar_lanzar()`, **antes** de que exista ninguna garantía de que el
efecto vaya a completarse. Es la misma decisión de diseño que 04 · 30 §5.7 toma con el ataque
cuerpo a cuerpo cuando rompe el aguante del rival: el riesgo es parte del sistema, no un bug
que arreglar con un reembolso automático.

### 3.5 Objetivo válido: uno mismo, aliado, enemigo en cono, área

`ObjetivoHabilidad` (§3.1) reutiliza el mismo trío de funciones que la selección en cono de
combate cuerpo a cuerpo —
[04 · 30 §4.9](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#49-selección-de-objetivo-en-cono):
`point_distance()`, `point_direction()` y `angle_difference()` — y el mismo patrón de `with`
anidado que ya usa el controlador de golpes en
[04 · 30 §5.6](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#56-el-controlador-detectar-encolar-resolver):
una variable local declarada fuera del `with` sigue siendo visible dentro de él.

```gml
// ---------------------------------------------------------------------------
// scr_habilidad_objetivo
// Verificado: point_distance, point_direction, angle_difference, abs,
//             instance_nearest, noone, infinity, with, continue
// ---------------------------------------------------------------------------

/// @func habilidad_objetivo_resolver(_def, _lanzador, _direccion_frente)
/// @desc Devuelve la instancia objetivo (o `noone`) según ObjetivoHabilidad.
///       NO decide si el lanzamiento procede: sólo busca a quién le tocaría.
/// @param {Struct} _def               Entrada de global.habilidades.
/// @param {Id.Instance} _lanzador
/// @param {Real} _direccion_frente    Grados. De dónde sale tu apuntado real
///                                    (image_angle, o el ángulo hacia el ratón
///                                    de 04 · 02 §4.3) es cosa de tu jugador,
///                                    no de este documento: se pasa como dato.
/// @returns {Id.Instance}
function habilidad_objetivo_resolver(_def, _lanzador, _direccion_frente)
{
    switch (_def.objetivo)
    {
        case ObjetivoHabilidad.UNO_MISMO:
        case ObjetivoHabilidad.AREA_EN_PUNTO:
            return _lanzador;   // el área usa `_punto` de intentar_lanzar(), no una instancia

        case ObjetivoHabilidad.ENEMIGO_MAS_CERCANO:
            return instance_nearest(_lanzador.x, _lanzador.y, _def.objeto_objetivo);

        case ObjetivoHabilidad.ENEMIGO_EN_CONO:
            var _mejor      = noone;
            var _mejor_dist = infinity;

            with (_def.objeto_objetivo)
            {
                var _dist = point_distance(_lanzador.x, _lanzador.y, x, y);
                if (_dist > _def.alcance) continue;

                var _dir_hacia = point_direction(_lanzador.x, _lanzador.y, x, y);
                if (abs(angle_difference(_dir_hacia, _direccion_frente)) > _def.cono_grados * 0.5)
                {
                    continue;
                }

                if (_dist < _mejor_dist) { _mejor_dist = _dist; _mejor = id; }
            }
            return _mejor;
    }
    return noone;
}
```

### 3.6 Enganchar el coste de estamina a la esquiva que ya existe en 04 · 30

[04 · 30 §5.8](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#58-el-jugador-combos-cancels-y-buffer)
ya deja el hueco marcado con un comentario textual: *«Cancelar a esquiva es lo que hace que el
combate no se sienta pegajoso. Coste: hay que gastar algo (stamina, recurso)»*. Esto es
exactamente ese coste, enganchado sin reescribir la FSM original — sólo se añaden las líneas
marcadas como NUEVO:

```gml
// obj_jugador — estados_del_jugador(), estado "quieto" y "atacando"
// (04 · 30 §5.8, TAL CUAL, con una comprobación añadida antes de consumir el buffer)

// quieto → update()
if (habilidades.puede_lanzar("esquiva_estamina") && buffer_esquiva.consume())   // NUEVO: la condición
{
    habilidades.intentar_lanzar("esquiva_estamina", id);                       // NUEVO
    fsm.set("esquiva");
    exit;
}
```

```gml
// El estado "esquiva" (04 · 30 §5.8) no cambia NADA de su lógica de movimiento
// o i-frames: el coste ya se cobró en intentar_lanzar() antes de entrar aquí.
// Si puede_lanzar() devolvió false, buffer_esquiva.consume() ni se llama, y la
// esquiva simplemente no ocurre — el jugador se queda en "quieto" sin gastar
// el buffer, así puede reintentar el frame siguiente si de repente hay estamina.
```

> 🔺 **El orden importa: `puede_lanzar()` va ANTES de `buffer_esquiva.consume()`, no después.**
> Si consumes el buffer primero y luego descubres que no hay estamina, el jugador pierde el
> input que había guardado sin conseguir nada a cambio — la esquiva ni ocurre ni el botón hizo
> nada. `&&` en GML es de cortocircuito: si `puede_lanzar()` es `false`, `consume()` no llega
> a ejecutarse.

### 3.7 Enganchar el efecto al pipeline de daño de 04 · 32

Cada `efecto()` de §3.1 es una función normal: dentro puede llamar a cualquier cosa ya
verificada de 04 · 30 y 04 · 32, exactamente como si fuera el código de un ataque más.

**Daño con tipo elemental** (bola de fuego) — construye una `_caja` con los mismos campos que
`recibir_golpe()` ya lee en
[04 · 30 §5.7](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#57-recibir_golpe--el-receptor)
y en su extensión de
[04 · 32 §5.7](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#57-recibir_golpe-extendido--dónde-se-engancha-el-pipeline),
y la pasa a la MISMA función — no hay un segundo camino de daño para las habilidades:

```gml
// ---------------------------------------------------------------------------
// scr_habilidad_efectos
// Verificado: point_direction, instance_exists, noone, with
// Requiere que el proyecto ya tenga la extensión de recibir_golpe() de
// 04 · 32 §5.7 (dano_resolver, DanoTipo): si no la tienes, esto sigue
// funcionando contra la versión base de 04 · 30 §5.7, sólo que ignora tipo
// y penetración (los añade con su propio valor neutro).
// ---------------------------------------------------------------------------

/// @func habilidad_efecto_bola_fuego(_lanzador, _objetivo)
function habilidad_efecto_bola_fuego(_lanzador, _objetivo)
{
    if (_objetivo == noone || !instance_exists(_objetivo)) return;

    var _dir  = point_direction(_lanzador.x, _lanzador.y, _objetivo.x, _objetivo.y);
    var _caja = {
        dano : 22, empuje : 4.0, elevacion : 0,
        hitstun : 14, blockstun : 8, rompe_aguante : 1,
        rompe_bloqueo : false,
        tipo : DanoTipo.FUEGO, penetracion : 0        // 04 · 32 §2.2 — campos opcionales
    };

    with (_objetivo)
    {
        recibir_golpe({ caja: _caja, atacante: _lanzador, victima: id, direccion: _dir });
    }
}
```

**Curación**, respetando el bloqueo tras recibir daño que ya define
[04 · 32 §5.9](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#59-curación-como-sistema-hot-y-el-bloqueo-en-combate)
— una habilidad de curación no necesita reinventar esa regla, sólo preguntarle:

```gml
/// @func habilidad_efecto_curacion(_lanzador)
function habilidad_efecto_curacion(_lanzador)
{
    if (!curacion_permitida(_lanzador.combate))          // 04 · 32 §5.9
    {
        fx_floating_text(_lanzador.x, _lanzador.y - 16, "¡No en combate!", c_gray);   // 04 · 15 §5.6
        return;
    }
    _lanzador.combate.curar(40);
}
```

**Grito de furia** (definitiva de área que gasta TODA la furia, no una cifra fija — la
excepción legítima al «coste fijo» de §1.2: el `coste: 50` de §3.1 es sólo el mínimo para
poder lanzarla, y el propio efecto decide cuánto se lleva):

```gml
/// @func habilidad_efecto_grito_furia(_lanzador, _punto)
function habilidad_efecto_grito_furia(_lanzador, _punto)
{
    var _def            = global.habilidades[$ "grito_furia"];   // para objeto_objetivo y alcance
    var _furia_gastada  = _lanzador.recursos.furia.actual;        // TODA la que quede
    var _bonus_dano     = 1 + (_furia_gastada / _lanzador.recursos.furia.maximo);   // 1.0x .. 2.0x
    _lanzador.recursos.furia.gastar(_furia_gastada);

    var _caja = {
        dano : round(30 * _bonus_dano), empuje : 8.0, elevacion : -4,
        hitstun : 20, blockstun : 10, rompe_aguante : 3,
        rompe_bloqueo : true,
        tipo : DanoTipo.FISICO, penetracion : 0.20
    };

    with (_def.objeto_objetivo)
    {
        if (point_distance(x, y, _punto.x, _punto.y) > _def.alcance) continue;
        recibir_golpe({ caja: _caja, atacante: _lanzador, victima: id,
                         direccion: point_direction(_punto.x, _punto.y, x, y) });
    }
}
```

**Ganar furia al golpear** se engancha en el mismo sitio donde 04 · 30 §5.6 ya resuelve la cola
de golpes — no en el `efecto()` de una habilidad, porque un ataque básico también debe generar
furia (§1.6, «*must be generated first in order to be usable*»):

```gml
// obj_combate — End Step, justo después del paso 10 de 04 · 30 §5.6
// ("Aplicar la cola → recibir_golpe()"). Todo lo anterior se queda igual;
// esta comprobación es NUEVA y va justo debajo de esa línea.
var _hizo_dano = recibir_golpe(_golpe);
if (_hizo_dano
&&  instance_exists(_golpe.atacante)
&&  variable_instance_exists(_golpe.atacante, "recursos"))
{
    _golpe.atacante.recursos.furia.ganar(10);      // FUENTE de furia — §1.5
}
```

**Un efecto de estado** (veneno en vez de daño directo) es todavía más corto, porque
`combate.efectos` ya hace todo el trabajo (04 · 32 §5.4):

```gml
/// @func habilidad_efecto_veneno(_lanzador, _objetivo)
function habilidad_efecto_veneno(_lanzador, _objetivo)
{
    if (_objetivo == noone || !instance_exists(_objetivo)) return;
    _objetivo.combate.efectos.aplicar("veneno", global.efecto_duracion.veneno);   // 04 · 32 §5.4/§5.5
}
```

### 3.8 Enganchar con el árbol de habilidades de 13 · 16

Una habilidad con `flag_requerido` no vacío (el `grito_furia` de §3.1) sólo debe poder lanzarse
—o incluso mostrarse activa en la barra— si el árbol de progresión ya la desbloqueó. El árbol
escribe ese flag exactamente en
[13 · 16 §3.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#34-enganchar-los-efectos-estadísticas-armadura-resistencias-y-keystones):
un nodo de tipo `NodoEfecto.HABILIDAD` hace `global.progreso[$ _ef.flag] = true` al comprarlo.
Este documento sólo **lee** ese mismo flag — no inventa un segundo sistema de desbloqueos:

```gml
// ---------------------------------------------------------------------------
// scr_habilidad_desbloqueo
// Verificado: variable_struct_exists, variable_global_exists
// ---------------------------------------------------------------------------

/// @func habilidad_desbloqueada(_clave)
/// @desc true si la habilidad no depende de ningún nodo (flag_requerido vacío,
///       caso normal), o si el árbol de 13 · 16 ya escribió su flag.
function habilidad_desbloqueada(_clave)
{
    var _def = global.habilidades[$ _clave];
    if (_def.flag_requerido == "") return true;

    if (!variable_global_exists("progreso")) return false;
    return variable_struct_exists(global.progreso, _def.flag_requerido)
        && global.progreso[$ _def.flag_requerido];
}
```

`puede_lanzar()` (§3.3) ya llama a esta función antes que a ninguna otra comprobación: una
habilidad no desbloqueada nunca llega a mirar enfriamiento, cargas ni recurso.

### 3.9 La barra de acción: slots, barrido radial e indicador de cargas

Construida sobre los mismos cuatro elementos que
[13 · 05 §3.5 a)](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#a-botón-con-sus-cuatro-estados)
ya define para un botón — `ancla()`, `aproximar()`, `panel_dibujar()`, el patrón struct +
`_actualizar()` + `_dibujar()` — y no un componente nuevo desde cero. Lo único que no existía
en esta biblioteca es el **barrido radial**: un abanico de triángulos (`pr_trianglefan`) que
tapa la fracción de enfriamiento que aún falta, empezando arriba y girando en sentido horario,
como las agujas de un reloj:

```gml
// ---------------------------------------------------------------------------
// scr_ui_barrido_radial
// Verificado: draw_primitive_begin, draw_primitive_end, draw_vertex_colour,
//             pr_trianglefan, lengthdir_x, lengthdir_y, clamp, ceil, min
// ---------------------------------------------------------------------------

/// @func dibujar_barrido_radial(_cx, _cy, _radio, _fraccion, _color, _alfa)
/// @desc Dibuja la porción de círculo AÚN CUBIERTA por el enfriamiento: a
///       _fraccion == 1 (recién lanzada) tapa el icono entero; a medida que
///       el enfriamiento baja, el hueco se abre en sentido horario desde
///       arriba, igual que un reloj de arena visto desde encima.
/// @param {Real} _fraccion  0 (lista) .. 1 (recién usada)
function dibujar_barrido_radial(_cx, _cy, _radio, _fraccion, _color, _alfa)
{
    _fraccion = clamp(_fraccion, 0, 1);
    if (_fraccion <= 0) return;

    static SEGMENTOS = 32;                       // suficiente para que no se note el polígono
    var _pasos = ceil(SEGMENTOS * _fraccion);

    draw_primitive_begin(pr_trianglefan);
    draw_vertex_colour(_cx, _cy, _color, _alfa);           // el centro es el pivote del abanico

    for (var _i = 0; _i <= _pasos; _i++)
    {
        var _t   = min(_i / SEGMENTOS, _fraccion);
        var _ang = 90 - (360 * _t);              // 90° = arriba; decrece → sentido horario
        draw_vertex_colour(_cx + lengthdir_x(_radio, _ang),
                            _cy + lengthdir_y(_radio, _ang), _color, _alfa);
    }
    draw_primitive_end();
}
```

Y el slot completo, con el mismo patrón `_nuevo / _actualizar / _dibujar` de 13 · 05 §3.5:

```gml
// ---------------------------------------------------------------------------
// scr_ui_slot_habilidad
// Verificado: draw_sprite_ext, draw_set_halign, draw_set_valign, draw_text,
//             fa_left, fa_right, fa_top, fa_bottom, string
//             (ancla(), aproximar() y panel_dibujar() son de 13 · 05 §3.2/§3.5)
// ---------------------------------------------------------------------------

/// @func slot_habilidad_nuevo(_clave, _fx, _fy, _mx, _my, _lado)
/// @desc El slot guarda su ANCLA, no su posición — mismo motivo que el botón
///       de 13 · 05 §3.5 a): sobrevive a cambiar de resolución.
function slot_habilidad_nuevo(_clave, _fx, _fy, _mx, _my, _lado)
{
    return { clave: _clave, fx: _fx, fy: _fy, mx: _mx, my: _my,
             lado: _lado, px: 0, py: 0, pulso: 1 };
}

/// @func slot_habilidad_actualizar(_s)
function slot_habilidad_actualizar(_s)
{
    var _p = ancla(_s.fx, _s.fy, _s.mx, _s.my);
    _s.px = _p.px;
    _s.py = _p.py;
    _s.pulso = aproximar(_s.pulso, 1, 0.06);
}

/// @func slot_habilidad_dibujar(_s, _gestor)
/// @param {Struct} _gestor  El GestorHabilidades de §3.3 del dueño de la barra.
function slot_habilidad_dibujar(_s, _gestor)
{
    var _def = global.habilidades[$ _s.clave];
    var _cx  = _s.px + _s.lado * 0.5;
    var _cy  = _s.py + _s.lado * 0.5;
    var _listo = (_gestor.enfriamiento[$ _s.clave] <= 0) && (_gestor.cargas[$ _s.clave] > 0);

    // 1. Panel de fondo (13 · 05 §3.4/§3.5): SIEMPRE debajo del icono.
    panel_dibujar(spr_panel_slot, _s.px, _s.py, _s.lado, _s.lado, c_white, 1);

    // 2. Icono, atenuado si no está desbloqueada (13 · 16) o sin recurso.
    var _visible = habilidad_desbloqueada(_s.clave);
    draw_sprite_ext(_def.icono, 0, _cx, _cy, _s.pulso, _s.pulso, 0,
                    c_white, _visible ? (_listo ? 1 : 0.6) : 0.25);
    if (!_visible) return;      // ni barrido ni cargas: el jugador no la tiene

    // 3. Barrido radial de enfriamiento — SOBRE el icono, oscurece lo que falta.
    if (_gestor.enfriamiento[$ _s.clave] > 0)
    {
        var _fraccion = _gestor.enfriamiento[$ _s.clave] / _def.enfriamiento;
        dibujar_barrido_radial(_cx, _cy, _s.lado * 0.5, _fraccion, c_black, 0.65);
    }

    // 4. Contador de cargas — sólo si la habilidad puede tener más de una.
    if (_def.cargas_max > 1)
    {
        draw_set_halign(fa_right);
        draw_set_valign(fa_bottom);
        draw_text(_s.px + _s.lado - 2, _s.py + _s.lado - 2, string(_gestor.cargas[$ _s.clave]));
        draw_set_halign(fa_left);
        draw_set_valign(fa_top);
    }
}
```

> 💡 **El color del barrido comunica sin texto.** Negro semitransparente («todavía tapado») es
> el mínimo honesto; si quieres un paso más, interpola el color hacia el color del recurso
> (naranja para furia, azul para maná) a medida que `_fraccion` baja — el jugador aprende a leer
> «ya casi» sin mirar un número. Ver
> [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) para el resto del *juice*
> de UI de combate (el pulso de `_s.pulso` de este struct ya sigue ese mismo patrón).

### 3.10 Qué se guarda y qué no

| Dato | ¿Se guarda? | Por qué |
|---|---|---|
| `cargas[$ clave]` | **Sí** | Es un recurso de partida: si el jugador cierra con 1 de 2 cargas, debe seguir teniendo 1 al volver a cargar |
| `enfriamiento[$ clave]` restante | **No** | Guardar «te quedan 40 F de enfriamiento» y cargarlo tras un tiempo real distinto es más confuso que ponerlo a 0: nadie espera que una partida cargada recuerde milisegundos exactos |
| `enfriamiento_global` | **No** | Mismo motivo; además, a 0 en cada carga es lo más seguro (nunca deja al jugador sin poder actuar el primer fotograma) |
| `recursos.*.actual` | **Sí** | Es tan de partida como la vida — usa el mismo `serialize()`/`deserialize()` de [04 · 04 §5.0](./04%20-%20RPG%20_%20Action%20RPG.md#50-estadísticas), añadiendo los campos nuevos |
| `flag_requerido` cumplido o no | **Ya se guarda** — es `global.progreso`, y ese guardado es responsabilidad de [13 · 16 §3.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#35-meta-progresión-persistente-guardado-versionado), no de este documento | No lo dupliques en un segundo campo |

```gml
/// @func gestor_habilidades_serializar(_g)
/// @desc Struct plano, listo para json_stringify() (01 · 14 §8). Los métodos
///       de GestorHabilidades NO se serializan (son funciones): por eso se
///       vuelca sólo lo que es dato, igual que Stats.serialize() en 04 · 04 §5.0.
function gestor_habilidades_serializar(_g)
{
    return { cargas: _g.cargas, recursos: {
        estamina: _g.recursos.estamina.actual,
        mana:     _g.recursos.mana.actual,
        furia:    _g.recursos.furia.actual
    }};
}
```

---

## 4 · Checklist

- [ ] Cada habilidad de `global.habilidades` tiene los seis campos de §1.2: coste,
      enfriamiento, cargas máx., casteo, interrumpible, objetivo.
- [ ] `puede_lanzar()` comprueba, EN ESTE ORDEN, casteo en curso → desbloqueo (13 · 16) → GCD →
      enfriamiento propio → cargas → recurso. El orden importa: comprobar el recurso antes que
      el desbloqueo gastaría ciclos en una habilidad que ni siquiera se tiene.
- [ ] El coste se cobra en `intentar_lanzar()`, no al final del casteo — una habilidad
      interrumpida no devuelve el recurso (§1.7, §3.4).
- [ ] Toda habilidad ofensiva llama a `recibir_golpe()` (04 · 30/04 · 32) en vez de restar vida
      a mano: un segundo camino de daño es, tarde o temprano, un enemigo inmune a la mitad de
      tu juego sin que nadie sepa por qué.
- [ ] `RecursoCombate` de furia tiene `regen_por_frame` **negativo** (decae) y un
      `retardo_frames` que le da un margen tras el último golpe (13 · 01 §4.3: todo recurso
      necesita un sumidero, y para la furia el sumidero es el propio decaimiento).
- [ ] La esquiva con recurso comprueba `puede_lanzar()` ANTES de consumir el buffer de input
      (§3.6): un botón pulsado sin estamina no debe "perderse" en el buffer.
- [ ] La barra de acción atenúa el icono en tres niveles distintos: no desbloqueada (25 %),
      desbloqueada pero sin recurso o en enfriamiento (60 %), lista (100 %) — nunca un único
      "gris/color".
- [ ] El barrido radial tapa desde arriba en sentido horario y se recalcula cada frame a partir
      de `enfriamiento[$ clave] / _def.enfriamiento`: nunca se anima con un tween aparte que
      pueda desincronizarse del valor real.
- [ ] Las cargas y los valores de los recursos se serializan; el enfriamiento restante y el GCD
      no (§3.10).
- [ ] Ninguna habilidad de esta lista es, en realidad, una habilidad-llave de Metroidvania
      (04 · 06 §4.2) ni un nodo de árbol (13 · 16) disfrazado: si no tiene coste NI
      enfriamiento, probablemente no pertenece a `global.habilidades`.

---

## 5 · Errores clásicos y cómo evitarlos

- **Cobrar el coste al final del casteo, no al principio.** Si el jugador cancela o le
  interrumpen, el recurso "nunca se gastó" y el sistema deja de tener riesgo: castear se
  vuelve gratis hasta que sale bien. Cóbralo en `intentar_lanzar()` (§3.4).
- **Un enfriamiento global que también afecta a la esquiva.** El GCD existe para poner ritmo
  entre HABILIDADES DE ATAQUE; si también bloquea esquivar, el jugador queda indefenso justo
  después de castear un hechizo — la esquiva de §3.1 lleva `usa_gcd: false` a propósito.
- **Furia (o cualquier recurso "ganado por acción") sin decaimiento ni techo real.** Se
  convierte en un número que sólo sube durante toda la partida y dejas de mirarlo: la regla de
  13 · 01 §4.3 ("todo recurso necesita un sumidero") se aplica también dentro de un solo
  combate, no sólo a la economía de la partida entera.
- **Cargas que recargan todas a la vez en vez de una por una.** Si al llegar a 0 cargas
  esperas `cargas_recarga` fotogramas y de repente tienes las `cargas_max` de golpe, el
  sistema deja de comunicar "estoy recuperando la primera de dos" — la secuencia de §3.3
  (un temporizador, uno detrás de otro) es la que sí lo comunica.
- **Dos caminos de daño distintos: uno para ataques cuerpo a cuerpo, otro "más rápido" para
  habilidades que resta vida directamente.** En cuanto añadas armadura, resistencias o un
  escudo (04 · 32), el camino rápido se vuelve la excepción que nadie recuerda revisar. Todo
  daño, sin excepción, pasa por `recibir_golpe()`.
- **Mostrar una habilidad en la barra antes de comprobar si está desbloqueada.** El jugador ve
  un icono, lo pulsa, y no pasa nada — peor que no mostrarlo, porque parece un bug del juego en
  vez de una habilidad que todavía no tiene. `slot_habilidad_dibujar()` corta en seco si
  `!habilidad_desbloqueada()` (§3.9).
- **Confundir el `coste` de una definitiva de "gástalo todo" con un coste fijo.** Si
  `intentar_lanzar()` sólo comprobara `hay_suficiente(coste)` y luego gastara literalmente
  `coste`, el grito de furia de §3.1 nunca aprovecharía la furia por encima del mínimo. El
  propio `efecto()` es quien decide cuánto se lleva cuando el coste es variable (§3.7).
- **Barrido radial dibujado con un `image_angle` o una animación de sprite en vez de
  recalculado del dato real cada frame.** En cuanto el juego se pause, se ralentice (*hit
  stop*, 04 · 15) o el enfriamiento cambie por un efecto externo, la animación y el dato real
  se desincronizan. `dibujar_barrido_radial()` no anima nada por sí sola: lee la fracción
  actual y la dibuja, fotograma a fotograma (§3.9).

---

## Ver también

- [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md) —
  el grafo que decide QUÉ habilidades tiene el jugador y con qué puntos las compró;
  `global.progreso` es el único punto de contacto (§3.8).
- [04 · 06 — Metroidvania](./06%20-%20Metroidvania.md) — las habilidades-llave (§4.2), la otra
  cosa que también se llama «habilidad» y con la que ésta no debe confundirse (§1.1).
- [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  `recibir_golpe()`, `DanoTipo`, `curacion_permitida()` y `combate.efectos`: el pipeline al que
  todo efecto ofensivo o curativo de este documento se engancha (§3.7).
- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md) —
  `EstadoCombate`, frame data, i-frames, la FSM del jugador y la selección de objetivo en cono
  (§4.9 de ese documento) sobre las que se construyen §3.5 y §3.6 de éste.
- [13 · 01 §4 — Economía y balance](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#4--economía-y-balance) —
  pool/fuente/sumidero/realimentación, la regla del sumidero obligatorio, y el TTK que §2.3
  reutiliza para el DPS efectivo.
- [13 · 05 §3.5 — Los componentes clásicos de UI](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#35-los-componentes-clásicos) —
  `ancla()`, `aproximar()`, `panel_dibujar()` y el patrón struct+actualizar+dibujar sobre el
  que se construye la barra de acción de §3.9.
- [04 · 04 — RPG / Action RPG](./04%20-%20RPG%20_%20Action%20RPG.md) — `Stats` con `mp`/`mp_max`
  (§5.0), con los que se sincroniza el maná de §3.2 en vez de duplicarlos.
- [04 · 34 — Combate a distancia: armas, munición y balística](./34%20-%20Combate%20a%20distancia%20-%20armas,%20munición%20y%20balística.md) —
  munición de armas de fuego, un recurso hermano de estamina/maná/furia pero fuera del alcance
  de este documento (§2.4).
- [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — `hit_complete()`,
  `fx_floating_text()` y el resto del feedback que un lanzamiento de habilidad debería disparar.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) —
  el patrón `serialize()`/`json_stringify()` que usa §3.10 para guardar cargas y recursos.

---

## Fuentes

**Diseño de recursos, enfriamientos y cargas** (todas consultadas el 2026-09-06 con WebFetch):

- **Cooldown**, wiki oficial de *League of Legends* — definición de *cooldown*, los cuatro
  tipos (normal, estático, por objetivo, con cargas) y la confirmación explícita de que el
  diseño del juego **no** usa ningún enfriamiento global — citas usadas en §1.3 y §1.4:
  <https://wiki.leagueoflegends.com/en-us/Cooldown>
- **Ability haste**, wiki oficial de *League of Legends* — la fórmula exacta
  `Cooldown Reduction = Haste/(100+Haste)` y el tope de 500 de *haste* (83,3 % de reducción) —
  citada en el aviso de §3.3: <https://wiki.leagueoflegends.com/en-us/Ability_haste>
- **Ability resource**, wiki oficial de *League of Legends* — la taxonomía de recursos
  (maná, energía, y la familia de «furia» con sus variantes por campeón), con las citas
  textuales sobre regeneración y decaimiento que fundamentan la tabla de arquetipos de §1.6:
  <https://wiki.leagueoflegends.com/en-us/Ability_resource>
- **Soulslike**, Wikipedia (en inglés) — la cita sobre gestión de estamina y *"animation
  priority"* (animaciones que no se pueden cancelar hasta terminar) usada en §1.7 para
  justificar la interrupción de casteo: <https://en.wikipedia.org/wiki/Soulslike>

**Biblioteca interna (base para todo el enganche de §3):**

- [13 · 01 §4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#4--economía-y-balance) —
  vocabulario de economía (Adams y Dormans, *Game Mechanics: Advanced Game Design*, 2012, ya
  citado y verificado en ese documento; no se repite la cita aquí).
- [04 · 30](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md) y
  [04 · 32](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) — frame data,
  `EstadoCombate`, `recibir_golpe()` y el pipeline de daño: ambos documentos citan sus propias
  fuentes (Infil's Fighting Game Glossary, Dustloop) sobre el vocabulario de combate, que este
  documento hereda sin repetir.
- [13 · 16](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md) —
  cita la página oficial de *Path of Exile* sobre Keystones y respec; este documento no la
  repite porque no trata el árbol, sólo el flag que produce.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`; todos los
símbolos verificados con `python3 "_indice/buscar.py" <símbolo>` contra el `GmlSpec.xml` del
runtime 2026.0.0.23):

- Primitivas de dibujo: `draw_primitive_begin`, `draw_primitive_end`, `draw_vertex_colour`,
  `pr_trianglefan` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_primitive_begin.htm
- Trigonometría de juego: `lengthdir_x`, `lengthdir_y`, `point_direction`, `point_distance`,
  `angle_difference` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance/lengthdir_x.htm
- `struct_foreach` — comprobada y **descartada a propósito** para los bucles de tick de §3.3:
  su propia página del manual advierte que el valor de cada miembro «no se pueden modificar
  desde ella», y `GestorHabilidades.tick()` necesita mutar los contadores —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/struct_foreach.htm
- La declaración `with` y el uso válido de `break`/`continue` dentro de ella (§3.5) —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Overview/Language_Features/with.htm

> ⚠️ **Lo que NO está verificado en este documento.** El valor concreto del enfriamiento
> global (1,5 s citado de memoria para MMO genéricos en §1.3) no se ha comprobado contra
> ninguna fuente primaria esta sesión: es un punto de partida, no un número canónico. Los
> nombres de sprites y sonidos (`spr_icono_bola_fuego`, `snd_furia_definitiva`,
> `spr_panel_slot`…) son marcadores de posición que hay que crear, igual que en el resto de la
> biblioteca. El código de este documento se ha verificado símbolo a símbolo con `buscar.py`
> y contra la lógica ya publicada de 04 · 30 y 04 · 32, pero **no se ha compilado en un
> proyecto GameMaker real**: antes de darlo por bueno, cópialo a un proyecto y pasa
> `gm-cli compile`.
