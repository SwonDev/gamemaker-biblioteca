# 44 · Bullet heaven, autobattler y deckbuilder

> **Dificultad:** media-alta · Tres géneros que en 2026 son los que más se clonan y los que
> menos receta propia tenían en esta biblioteca: cada uno era, hasta este documento, **una
> fila de tabla** (`04 · 09 §1` para *bullet heaven*, `04 · 13 §1` para autobattler; el
> deckbuilder no tenía ni eso). Van en un único archivo porque los tres comparten un mismo
> esqueleto de diseño — bucle de rondas u oleadas, construcción de *build* durante la partida,
> economía de mejora entre rondas, escalado numérico agresivo — aunque se jueguen de formas
> irreconociblemente distintas entre sí. `§0` explica ese esqueleto una sola vez; `§1`, `§2` y
> `§3` lo aplican a cada género con su propia visión general, arquitectura, bucle, sistemas y
> código.
>
> **Qué NO cubre este documento** (y dónde está, para no repetirlo):
> - El **pipeline de daño y efectos de estado** (tipos, resistencias, veneno, aturdimiento) es
>   de [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md).
>   Aquí se **usa** `dano_resolver()`, no se reescribe.
> - Los **enfriamientos, cargas y recursos de una habilidad activa** (maná, estamina, furia)
>   son de [04 · 36 — Habilidades, enfriamientos y recursos de combate](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md).
>   El `ArmaEstado` de `§1` es más simple a propósito: en *bullet heaven* nadie pulsa un botón
>   para lanzar un arma.
> - El **árbol de habilidades permanente entre partidas**, la meta-progresión de poder frente
>   a opciones y el patrón de **monedas múltiples** (partida frente a meta) son de
>   [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades%2C%20desbloqueos%20y%20meta-progresión.md).
>   Este documento solo señala **dónde** se engancha cada género con ese sistema.
> - El **vocabulario de economía** (*pool*, fuente, sumidero, convertidor, realimentación, la
>   regla del sumidero obligatorio) es de
>   [13 · 01 §4 — Economía y balance](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#4--economía-y-balance).
>   Los tres géneros de este documento lo **aplican** sin repetirlo.
> - **RNG con semilla, generador propio y reproducibilidad** son de
>   [04 · 05 §4.1 y §5.0 — Roguelike y generación procedural](./05%20-%20Roguelike%20y%20generación%20procedural.md#41-rng-con-semilla).
>   Los tres géneros reutilizan el constructor `RNG()` de ese documento tal cual.
> - El *object pooling* genérico es de
>   [`06 - Assets y Scripts/scr_pool.gml`](<../06 - Assets y Scripts/scr_pool.gml>) y su
>   aplicación a proyectiles masivos, de
>   [04 · 03 §4.5-4.7 — Shoot 'em up](./03%20-%20Shoot%20em%20up%20%28shmup%29.md#45-object-pooling-obligatorio).
>   `§1.4.5` los enlaza para el problema de miles de enemigos; no los repite.
> - El **particionado espacial** para cientos de entidades es de
>   [13 · 08 §4 — Físicas a mano y fluidos](<../13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md#4--particionado-espacial-colisiones-cuando-hay-cientos-de-cosas>).
>   `§1.4.5` lo cita para el caso extremo; el caso normal se resuelve con funciones nativas.
> - El **combate cuerpo a cuerpo con hitboxes/hurtboxes reales** (para un *deckbuilder* con
>   combate visual en tiempo real en vez de resuelto por datos) es de
>   [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md).
>   Los tres géneros de aquí resuelven el combate **por datos**, no por colisión de cajas.

---

## 0 · El esqueleto que comparten los tres géneros

### 0.1 · Por qué van en el mismo documento

*Vampire Survivors*, *Teamfight Tactics* y *Slay the Spire* no se parecen en la pantalla: uno
es una horda que corre hacia ti, otro es un tablero hexagonal con figuritas, el tercero es un
mazo de cartas ilustradas. Pero los tres resuelven el mismo problema de diseño con la misma
forma:

| Pieza del esqueleto | Bullet heaven | Autobattler | Deckbuilder |
|---|---|---|---|
| **Unidad de tiempo** | Oleada (por tiempo o por XP) | Ronda | Combate / turno |
| **La build se arma jugando** | Elegir 1 de 3 armas/mejoras al subir de nivel | Comprar y fusionar unidades entre rondas | Elegir 1 de 3 cartas tras ganar un combate |
| **Economía que paga la build** | XP (implícita, sin gasto activo) | Oro con reroll e interés | Oro de evento/tienda entre combates |
| **Quién decide el orden** | El motor (aleatorio ponderado) | El jugador (qué comprar y cuándo) | El jugador (qué carta llevarse) |
| **Escalado de la amenaza** | Curva de tiempo: más enemigos, más vida | Curva de ronda: el enemigo también mejora | Curva de acto: encuentros más duros, jefes |
| **Fin de la partida** | Superviviente hasta el reloj, o muerto | Últimos en pie, o eliminado | Cima de la Spire, o muerto |

La consecuencia práctica: **la arquitectura de datos es casi intercambiable**. Un catálogo de
opciones ponderado por rareza, una función que aplica un efecto declarado en un struct, y un
contador que sube el multiplicador de dificultad — eso vale para las tres armas de un *bullet
heaven*, las cartas de un *deckbuilder* y las unidades de la tienda de un autobattler. Por eso
`§1.5`, `§2.5` y `§3.5` usan literalmente el mismo patrón de struct-catálogo + selección
ponderada + resolución por datos, solo con los campos que cambian.

### 0.2 · Bucle de rondas u oleadas

Los tres géneros tienen un **reloj de partida** que no es el mismo reloj que el de la acción
momento a momento (la distinción de
[13 · 01 §2.1 — Los tres relojes](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#21--los-tres-relojes)):

- **Bullet heaven**: el reloj de sesión (12-30 min) marca oleadas por tiempo; dentro de cada
  oleada el jugador no hace casi nada salvo moverse — el disparo ya lo resuelve el motor
  (`§1.3`).
- **Autobattler**: el reloj de partida son las rondas (15-30 en una partida de *Teamfight
  Tactics*); dentro de cada ronda hay una fase de preparación (el jugador decide) y una fase de
  combate (el motor decide, `§2.3`).
- **Deckbuilder**: el reloj de partida es la ruta por el mapa (un *acto* de *Slay the Spire*);
  dentro de cada combate hay turnos, y dentro de cada turno el jugador decide qué cartas jugar
  con el maná disponible (`§3.3`).

En los tres, **la fase de decisión y la fase de resolución están separadas**: el jugador arma
la build cuando el reloj se lo permite (subir de nivel, fase de preparación, fin de combate) y
el resto del tiempo la build ya está fijada y solo se ejecuta. Esto simplifica la arquitectura:
el estado de la build es una snapshot inmutable durante la resolución, así que la resolución
puede ser tan barata o tan determinista como haga falta (`§2.4.5`, `§3.4.2`).

### 0.3 · Construcción de *build* durante la partida, no antes

A diferencia de un RPG (`04 · 04`) donde el equipo se elige en un menú de inventario persistente,
en los tres géneros de este documento **la build nace vacía en cada partida y se completa
jugando**. Esto tiene dos consecuencias de diseño que hay que decidir pronto:

1. **El catálogo de opciones es mucho más grande que lo que una partida puede usar.** *Vampire
   Survivors* tiene más de 20 armas; una build típica usa 6. *Slay the Spire* tiene cientos de
   cartas; un mazo final tiene 15-25. El generador de opciones (`§1.4.3`, `§2.4.2`, `§3.4.5`) no
   enseña el catálogo entero: enseña un muestreo pequeño y ponderado, cada vez.
2. **La sinergia entre piezas importa más que el poder de una pieza sola.** Dos armas mediocres
   que se combinan bien ganan a una excelente sola. El diseño de las opciones (`§1.4.1`,
   `§2.4.4`, `§3.4.3`) tiene que dejar hueco para que existan combinaciones, no solo curvas de
   daño que suben en línea recta.

### 0.4 · Economía de mejora entre rondas

Cada género tiene su propia moneda (XP, oro, oro-de-tienda) pero las tres son la misma pieza del
vocabulario de
[13 · 01 §4.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#41--el-vocabulario-correcto):
un **pool** que se llena con una **fuente** (matar enemigos, ganar una ronda, ganar un combate)
y se vacía con un **sumidero** (comprar una mejora, un reroll, una carta). La regla que evita el
80 % de los desastres —
[13 · 01 §4.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#43--la-regla-que-evita-el-80--de-los-desastres-de-economía)—
aplica igual: si la moneda de la partida no tiene sumidero, deja de significar nada, y en estos
tres géneros el sumidero **es la build misma**: cada subida de nivel, cada compra, cada carta
elegida es un gasto que reinicia el ciclo fuente→sumidero.

La diferencia entre los tres está en **quién decide cuándo gastar**:

| | Control del gasto | Efecto |
|---|---|---|
| Bullet heaven | Ninguno: la mejora es obligatoria al llegar a la XP | La economía es un metrónomo, no una decisión |
| Autobattler | Total: guardar oro para interés, o gastarlo en reroll | La economía **es** el juego de mitad de partida |
| Deckbuilder | Parcial: elegir 1 de 3 tras ganar, y qué comprar en la tienda | La economía decide la forma del mazo, no su ritmo |

### 0.5 · Escalado numérico

Los tres necesitan que la amenaza crezca más deprisa que el poder del jugador, o la partida se
alarga sin tensión (`04 · 05 §4.7`, `13 · 01 §3.2`). Las cinco formas de curva y su lectura
están ya resueltas en
[13 · 13 §8 — Curvas de crecimiento para diseño](<../13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md#8--curvas-de-crecimiento-para-diseño>);
lo que aporta cada bloque de este documento es **qué variable concreta escala con qué curva**
en cada género (`§1.4.2`, `§2.4.3`, `§3.4.4`), no la teoría general de curvas, que no se repite
aquí.

### 0.6 · Qué NO comparten

No fuerces una arquitectura única solo porque el esqueleto se parece:

- **La resolución del combate es opuesta.** *Bullet heaven* resuelve daño en tiempo real,
  frame a frame, contra cientos de instancias (`§1.4.5`). Autobattler resuelve un combate
  entero en unos pocos frames de simulación, sin dibujar cada golpe si no hace falta (`§2.4.5`).
  Deckbuilder resuelve un golpe por decisión explícita del jugador, con energía limitada
  (`§3.3`). No copies el bucle de uno para el otro.
- **El input del jugador es de naturaleza distinta.** Movimiento continuo (bullet heaven),
  colocación espacial discreta (autobattler), selección de una lista (deckbuilder). La UI de
  cada uno se diseña por separado; no hay un «panel de build» genérico que sirva para los tres.
- **La aleatoriedad cumple papeles distintos.** En autobattler el RNG de la tienda **es** el
  reto (gestionar la varianza es la habilidad central). En deckbuilder el RNG del mazo se
  **mitiga** con decisiones de diseño de mazo (adelgazarlo, ver la carta siguiente). En bullet
  heaven el RNG casi no se nota: las mejoras se aceptan casi todas, así que su peso importa más
  que su presencia.

---

## 1 · Bullet heaven (*Vampire Survivors*)

### 1.1 · Visión general

Un *bullet heaven* invierte el *bullet hell* (`04 · 03`): en vez de que el jugador esquive
miles de balas enemigas mientras dispara con cuidado, es **el jugador quien inunda la pantalla**
de proyectiles automáticos mientras esquiva una horda que crece sin parar. El término lo acuñó
la comunidad tras el éxito de *Vampire Survivors* (poncle, 2022) para diferenciarlo del *bullet
hell* clásico — el propio *Vampire Survivors* se describe en su ficha oficial como «a time
survival game with minimalistic gameplay and roguelite elements» donde «all you can do is try
to survive a cursed night and get as much gold as possible for the next survivor»
(<https://poncle.itch.io/vampire-survivors>, consultado 2026-09-06). Esa frase resume las tres
piezas del género: supervivencia por tiempo, mecánica mínima, y una moneda que sobrevive a la
muerte del personaje (la meta-progresión de `13 · 16 §2.4`).

**Lo que define al género, frente a lo que ya cubre la biblioteca:**

- **El jugador nunca apunta ni dispara.** Las armas tienen temporizador propio y eligen
  objetivo solas (`§1.4.1`). Esto es lo que lo separa de `04 · 02` (Top-Down/Twin-Stick), donde
  el jugador SÍ apunta con el ratón o el stick derecho.
- **Las oleadas no son discretas: son una curva continua de dificultad** (`§1.4.2`), a
  diferencia de `04 · 03`, donde `WaveDef` define oleadas con principio y fin explícitos.
- **La build se elige, no se fabrica.** No hay crafteo ni recolección de materiales: subir de
  nivel abre una elección entre 3 opciones y se acabó (`§1.4.3`). Esto lo diferencia de `04 · 09`
  (Survival y crafting), con el que se confunde por el nombre «supervivencia» — `04 · 09` es
  gestionar hambre/sed/temperatura sin amenaza activa; esto es sobrevivir a una horda.
- **El problema de ingeniería central no es la IA ni el control: es el volumen.** Cientos de
  enemigos, cientos de proyectiles propios, docenas de recogibles de experiencia, todos a la
  vez, en un motor 2D. `§1.4.5` es la sección más importante del bloque.

**Referencias:** *Vampire Survivors* (poncle, 2022), *Brotato* (Blobfish, 2023), *Halls of
Torment* (Chasing Carrots, 2023). En GameMaker, YoYoGames publica una plantilla oficial del
género — ver `§1.4.2` y `§1.7`.

### 1.2 · Arquitectura recomendada

```
obj_jugador          Movimiento, vida, XP, nivel, contenedor de ArmaEstado activas
obj_enemigo          (pool — MILES a lo largo de la partida, docenas vivas a la vez)
obj_proyectil_jugador (pool — igual que 04 · 03 §4.5, pero disparados sin input)
obj_recogible_xp     (pool — gemas de experiencia que caen de los enemigos)
obj_director_oleadas  Un único controlador: decide qué y cuánto spawnear, y cuándo sube el nivel
obj_pantalla_mejora   Aparece al subir de nivel; construida sobre 13 · 05 (paneles, botones)
```

**Structs (dirigidos por datos, sin lógica dentro):**

```
ArmaDef        catálogo estático: una entrada por arma disponible en el juego
ArmaEstado     una instancia de ArmaDef que el jugador lleva equipada, con su nivel actual
MejoraOpcion   una fila del menú de "elige 1 de 3": a qué arma o pasiva afecta, y cuánto
```

**Capas de la room:** `Fondo` (tileable, se repite si el jugador se aleja del centro) →
`RecogiblesXP` → `Enemigos` → `Jugador` → `ProyectilesJugador` → `UI`. El orden de dibujado
importa poco aquí porque casi todo usa `depth = -y` para el orden top-down habitual de `04 · 02`.

Los tres "pool" de arriba son `Pool` de verdad
([`06/scr_pool.gml`](<../06 - Assets y Scripts/scr_pool.gml>) §USO RÁPIDO), y `global.semilla_combate`
(§1.4.2 y §1.5) tiene que existir antes del primer enemigo — sin esto, todo lo que sigue en este
documento lee un `global.pool_*`/`global.semilla_combate` que nunca se creó:

```gml
/// obj_director_oleadas · Create — antes de spawnear el primer enemigo
global.pool_enemigos            = new Pool(obj_enemigo, 200, "Enemigos");
global.pool_proyectiles_jugador = new Pool(obj_proyectil_jugador, 300, "ProyectilesJugador");
global.pool_recogibles_xp       = new Pool(obj_recogible_xp, 150, "RecogiblesXP");
global.semilla_combate          = irandom(999999);   // fija por partida; guárdala si quieres replays
```

### 1.3 · El bucle central

```
┌─ Cada frame ──────────────────────────────────────────────┐
│ 1. Mover al jugador según input (sin disparo manual)       │
│ 2. Actualizar cada ArmaEstado del jugador: temporizador--; │
│    si llega a 0, disparar sola y resetear temporizador      │
│ 3. Actualizar enemigos activos: perseguir al jugador        │
│ 4. Resolver colisiones proyectil↔enemigo, jugador↔enemigo   │
│ 5. Enemigos muertos → soltar recogible de XP                │
│ 6. Jugador recoge XP dentro de su radio de imán             │
│ 7. obj_director_oleadas: ¿toca spawnear? ¿XP ≥ meta?         │
│    → si XP ≥ meta: pausar, mostrar 3 mejoras, aplicar        │
│      la elegida, avanzar oleada (curva más dura)             │
└──────────────────────────────────────────────────────────┘
```

La clave que lo diferencia de un *shmup* (`04 · 03 §3`): **no hay paso de "leer input de
disparo"**. El único input del jugador es movimiento; todo lo ofensivo pasa por el paso 2, sin
que el jugador lo dispare.

### 1.4 · Sistemas clave

#### 1.4.1 · Armas que disparan solas

Cada arma equipada es un `ArmaEstado` con su propio temporizador, independiente del framerate en
fotogramas igual que el resto de la biblioteca (`ENFRIAMIENTO_GLOBAL_FRAMES` de `04 · 36 §3.1`
usa el mismo patrón). En el `Step` del jugador, cada arma resta su temporizador y dispara sola
cuando llega a 0 — el jugador no interviene en absoluto. La elección de objetivo suele ser una de
estas tres, y conviene mezclarlas entre armas para que no todas se sientan igual:

| Selección de objetivo | Cuándo usarla | Coste |
|---|---|---|
| Enemigo más cercano (`instance_nearest`) | Arma de proyectil único (la primera del jugador) | Barato: una llamada |
| Dirección fija u orbital (gira alrededor del jugador) | Armas de área continua | Ninguno: no busca objetivo |
| Aleatoria dentro de un radio | Armas de "lluvia" (caen del cielo en zonas al azar) | Barato: `random_range` sobre el radio |

#### 1.4.2 · Oleadas por tiempo o por nivel: dos aproximaciones reales

Hay dos formas de dirigir la dificultad, y las dos son legítimas — la diferencia es si la curva
depende del **reloj de partida** o de la **XP acumulada**.

**A) Curva por tiempo** (la aproximación de *Vampire Survivors*): un temporizador de sesión
(20-30 min) dirige qué enemigos pueden aparecer y con qué frecuencia, igual que `WaveDef` en
`04 · 03 §5.2` pero sin oleadas discretas — es una tabla de "minuto → probabilidad de spawn por
tipo", consultada continuamente.

**B) Curva por nivel del jugador** (la aproximación de la plantilla oficial de GameMaker): cada
vez que el jugador sube de nivel, el juego avanza a la "siguiente oleada" y **todos los
parámetros de dificultad suben de golpe en ese instante**, no de forma continua. Se ha verificado
descargando el paquete real de la **Survivor Game Template** que distribuye YoYoGames — API
oficial `https://api.gamemaker.io/api/gamemaker/project-templates`, plantilla `info_title:
"Survivor Game Template"`, descripción oficial: *"Build a Survivor game with the GameMaker Farm
Survivor Template Project"* (verificado el 2026-09-06 descargando el paquete
`com.gamemaker.farmsurvivorcode` v1.0.3 con `gm-cli` y leyendo su GML). Su función
`next_wave()`, completa:

```gml
// Función real de la Survivor Game Template oficial (objeto obj_game, script next_wave).
// Se cita literalmente porque es la fuente primaria del patrón "curva por nivel".
function next_wave()
{
    global.xp -= global.xp_goal;                              // coste de la subida
    global.xp_goal = floor(global.xp_goal * 1.2);              // meta de XP: geométrica, razón 1,2
    global.enemy_spawn_speed -= 3;                              // spawnea cada vez más seguido
    global.enemy_health_bonus = global.enemy_health_bonus * 1.25; // enemigos más duros
}
```

Es exactamente la **curva de coste geométrica** de
[13 · 01 §4.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#curva-de-coste-geométrica)
aplicada dos veces (a la meta de XP y a la vida enemiga), y una resta lineal aplicada a la
tercera (velocidad de spawn). La plantilla limita la partida a **10 oleadas** (`global.level ==
10` dispara la pantalla de "plantilla completada") y añade enemigos nuevos por nivel en vez de
solo escalar los que ya había: por debajo del nivel 2 solo aparece un tipo de enemigo, entre 2 y
4 se suma un segundo tipo, y por encima de 4 un tercero — variedad que crece con el tiempo, no
solo números que suben.

El *spawn* en sí evita aparecer dentro de la cámara: genera la posición a 1200 px del jugador en
una dirección al azar y, si esa posición sigue cayendo dentro de la vista de la cámara, la aleja
400 px más en la misma dirección hasta salir de cuadro — así el enemigo nunca aparece
literalmente encima del jugador ni desaparece de la nada frente a sus ojos:

```gml
// Adaptado del spawn_enemy() real de la Survivor Game Template.
function spawn_enemigo_fuera_de_camara(_obj_enemigo)
{
    var _dir = random(360);
    var _dist = 1200;
    var _x = obj_jugador.x + lengthdir_x(_dist, _dir);
    var _y = obj_jugador.y + lengthdir_y(_dist, _dir);

    var _vista = view_camera[view_current];
    while (camera_get_view_x(_vista) - 100 < _x && _x < camera_get_view_x(_vista) + camera_get_view_width(_vista)  + 100
        && camera_get_view_y(_vista) - 100 < _y && _y < camera_get_view_y(_vista) + camera_get_view_height(_vista) + 100)
    {
        _dist += 400;
        _x = obj_jugador.x + lengthdir_x(_dist, _dir);
        _y = obj_jugador.y + lengthdir_y(_dist, _dir);
    }

    return global.pool_enemigos.get_at(_x, _y, _obj_enemigo);
}
```

⚠️ Esta función asume una `Pool` que sabe crear más de un tipo de objeto (variante de
`06 - Assets y Scripts/scr_pool.gml`, que asume un solo `obj` por pool — para varios tipos de
enemigo, usa un `Pool` por tipo y elige cuál llamar antes, como hace `choose(obj_pigun,
obj_pumpkill)` en la plantilla oficial).

**Cuál elegir:** la curva por tiempo da sesiones de longitud fija y previsible (mejor para
*speedrunning* y comparar partidas). La curva por nivel da sesiones que se alargan si el jugador
juega mejor (sube de nivel más despacio si no consigue XP) — mejor para una primera partida sin
reloj visible. Ninguna es "la correcta"; *Vampire Survivors* usa la primera, la plantilla
oficial de GameMaker usa la segunda.

#### 1.4.3 · Subida de nivel: elegir 1 de 3

Al llegar a la meta de XP se muestran opciones — 3 es el estándar del género (la plantilla
oficial también usa `min(_size, 3)`). El generador:

1. Reúne **todas** las mejoras disponibles ahora mismo (armas no desbloqueadas primero: si una
   ranura de arma sigue vacía, desbloquearla debería tener más peso que subir de nivel una que
   ya está al máximo).
2. Baraja la lista completa (`array_shuffle`, o el `RNG.shuffle()` de `04 · 05 §5.0` si la
   partida necesita semilla reproducible — ver `§1.7`).
3. Toma las primeras 3 (o menos, si el jugador ya tiene casi todo maximizado).

No hay **reroll** en el diseño original de *Vampire Survivors* (las 4 opciones que ofrece son
las que son); la Survivor Game Template oficial sí añade un botón de reroll **gratuito** — vuelve
a llamar a la misma función generadora sin coste ni límite de usos. Si tu diseño quiere que el
reroll cueste algo, dale un precio en la propia moneda de XP (un sumidero más, coherente con
`13 · 01 §4.3`) en vez de dejarlo gratis: gratis, el reroll dejar de ser una decisión y se
convierte en "repetir hasta que salga lo que quiero".

#### 1.4.4 · Evoluciones

Una **evolución** fusiona un arma al nivel máximo con una pasiva concreta en una versión más
fuerte y distinta, no solo "el arma pero con más números" — es el gancho de variedad que hace que
dos partidas con las mismas armas iniciales terminen jugándose distinto. *Vampire Survivors* lo
describe como fusionar el arma base con su pasiva («*Bloody Tear*, evolution for the Whip»,
«*Heaven Sword*, evolution for the Cross» — <https://poncle.itch.io/vampire-survivors>,
consultado 2026-09-06). El requisito habitual son tres condiciones a la vez:

```gml
/// @func puede_evolucionar(_arma_estado, _inventario_pasivas)
/// @desc Condición estándar del género: arma a nivel máximo + pasiva concreta poseída
///       + (opcional) un objeto especial recogido en el mapa.
function puede_evolucionar(_arma_estado, _inventario_pasivas)
{
    var _def = _arma_estado.def;
    if (_arma_estado.nivel < ARMA_MAX_NIVEL) return false;
    if (!variable_struct_exists(_def, "evoluciona_con")) return false;
    return array_contains(_inventario_pasivas, _def.evoluciona_con);
}
```

Cuando se cumple, el motor sustituye el `ArmaEstado` original por uno nuevo con
`id_arma = _def.evolucion` (otra entrada del mismo catálogo de `§1.5`) en vez de seguir subiendo
números — la evolución **reemplaza**, no se suma.

#### 1.4.5 · El problema real de miles de entidades

Esta es la razón de ser técnica del género. Una partida de 20 minutos puede llegar a **cientos
de enemigos vivos a la vez** y **miles a lo largo de la partida completa**, más sus proyectiles y
recogibles de XP. `instance_create_layer()` + `instance_destroy()` sin control produce exactamente
el problema que describe
[`06 - Assets y Scripts/scr_pool.gml`](<../06 - Assets y Scripts/scr_pool.gml>):
tirones de framerate por creación/destrucción continua. La solución **es la misma que la de
`04 · 03 §4.5`** para las balas de un *shmup*, aplicada ahora a enemigos:

- Un `Pool` (o uno por tipo de enemigo, si varían mucho en tamaño de struct) pre-creado al
  empezar la partida — no dentro del bucle de spawn.
- `pool.release(id)` en vez de `instance_destroy()` cuando un enemigo muere.
- `pool.release_all()` al reiniciar tras morir, para no dejar huérfanos.

**El siguiente cuello de botella, cuando el pooling ya no basta:** con cientos de enemigos vivos,
las funciones nativas de colisión (`instance_place`, `collision_circle_list`) siguen siendo la
opción correcta **mientras los enemigos sigan siendo instancias de GameMaker** — el motor ya las
optimiza internamente, y es la recomendación explícita de
[13 · 08 §4.3](<../13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md#43-cuándo-compensa-y-cuándo-no>):
*"las funciones nativas son la primera opción cuando tus entidades son instancias"*. Solo si de
verdad necesitas ir más allá de lo que las instancias aguantan (varios miles simultáneos,
representados como *structs* ligeros en vez de objetos completos, para ahorrar el coste por
instancia) el **spatial hash** de
[13 · 08 §4.1](<../13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md#41-el-spatial-hash-una-rejilla-de-cubos>)
(`rejilla_nueva`, `rejilla_insertar`, `rejilla_vecinos`) es la única alternativa nativa que no
existe — no lo repitas aquí, ve directo a esa sección si llegas a ese punto.

**Otros costes que aparecen antes que la colisión, y que se resuelven con las mismas
herramientas del género:**

| Coste | Síntoma | Arreglo |
|---|---|---|
| `Draw` de cientos de sprites con `image_alpha`/tinte distinto | Caída de FPS proporcional al número visible | Culling agresivo: no dibujar lo que está fuera del margen de cámara + margen |
| IA de "todos persiguen al jugador" recalculando `point_direction` cada frame | Coste lineal, no cuadrático — molesta menos de lo que parece, pero suma | Tick escalonado (`04 · 31 §…`, actualizar la mitad de los enemigos en frames pares) si hace falta |
| Cientos de recogibles de XP con imán activo | Cada uno comprueba distancia al jugador cada frame | Radio de imán como comprobación barata (`point_distance` sin raíz cuadrada: comparar cuadrados, `13 · 13 §2.1`) |

#### 1.4.6 · Imán de recogida y daño de área masivo

Los recogibles de XP se mueven hacia el jugador cuando entran en su radio de imán — no antes:

```gml
/// obj_recogible_xp · Step
if (!activo) exit;   // instancia del pool, esperando a que la reciclen

var _radio_iman = obj_jugador.radio_iman;   // stat de la build, sube con mejoras (§1.4.3)
if (point_distance(x, y, obj_jugador.x, obj_jugador.y) < _radio_iman)
{
    move_towards_point(obj_jugador.x, obj_jugador.y, 12);
}
```

Las armas de área (auras, explosiones periódicas) no comprueban colisión contra cada enemigo con
`place_meeting`: barren con `collision_circle_list` (ver el patrón exacto en
[13 · 08 §4.3](<../13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md#43-cuándo-compensa-y-cuándo-no>))
y aplican `dano_resolver()` de `04 · 32 §5.1` a toda la lista de una vez, en vez de un bucle
`with (obj_enemigo)` que recorre TODOS los enemigos vivos aunque estén lejos.

#### 1.4.7 · Legibilidad a escala: qué te está matando

§1.4.5-1.4.6 resuelven el **coste** de tener cientos de enemigos en pantalla. Ninguna de las dos
dice cómo **lee** el jugador esa pantalla — y con cientos de proyectiles y enemigos superpuestos,
«¿qué me está matando?» es una pregunta real que el juego tiene que responder en menos de un
vistazo, no solo mantener a 60 fps.

**Silueta reservada para lo peligroso.** El shader de contorno de
[08 · 06 §6.2](<../08 - Referencia GML completa/06 - Shaders.md#62-contorno-outline>) ya existe
para dar relieve a un sprite — aquí se usa distinto: un `u_color_borde` que **ningún elemento
decorativo del juego use nunca** (magenta puro, `make_color_rgb(255, 0, 255)`, es la elección
clásica precisamente porque no aparece en paletas naturales) reservado en exclusiva para el
proyectil o el ataque que hace daño de verdad. Todo lo demás — enemigos de fondo, decoración,
partículas ambientales — se queda sin ese color, sin excepción.

```gml
// obj_proyectil_enemigo — Draw: el contorno es la señal, no la decoración
shader_set(sh_outline);
shader_set_uniform_f(u_texel, texture_get_texel_width(_tex), texture_get_texel_height(_tex));
shader_set_uniform_f(u_color_borde, 1.0, 0.0, 1.0);   // magenta: EXCLUSIVO de "esto te mata"
shader_set_uniform_f(u_grosor, 1.5);
draw_self();
shader_reset();
```

**Regla de exclusividad cromática, no solo de proyectiles.** El mismo principio se aplica a toda
la jerarquía visual: si el jugador usa un color para su barra de vida, ningún enemigo se tiñe con
él; si un enemigo de élite se marca con un color propio, ningún efecto ambiental lo repite. Con
200 sprites en pantalla, el color deja de ser estética y pasa a ser el único canal que sigue
funcionando cuando ya no hay tiempo de leer formas.

**Atribuir el daño: `ultimo_atacante`.** El número flotante de
[04 · 15 §5.6](<./15 - Game feel y juice.md#56-flash-de-impacto-y-texto-flotante>) dice CUÁNTO
dolió; con 40 enemigos disparando a la vez no dice QUIÉN. Guardarlo es una variable, no un
sistema nuevo — añádelo donde tu pipeline de daño ya conozca el origen del golpe, sin tocar la
firma de `hit_complete()` (04 · 15 §5.7):

```gml
// obj_jugador — guarda quién causó el último golpe
ultimo_atacante = _origen;
```

```gml
// fx_floating_text() (04 · 15 §5.6) etiqueta la fuente sin tocar su firma
var _texto = string(_dano);
if (instance_exists(ultimo_atacante)) _texto += " (" + object_get_name(ultimo_atacante.object_index) + ")";
fx_floating_text(x, y - 16, _texto, c_yellow);
```

> 💡 Con cientos de enemigos genéricos —el propio género de este documento— etiquetar CADA golpe
> recibido sería ruido, no lectura. `ultimo_atacante` vale más para el jefe o el enemigo especial
> que se esconde entre la masa («me está matando ESE, no el enjambre») que para el enjambre en
> sí.

### 1.5 · Código base

#### 1.5.0 · Catálogo de armas y struct de estado

```gml
// ---------------------------------------------------------------------------
// scr_armas_config
// Catálogo dirigido por datos, mismo patrón que WeaponDef (04 · 34 §5.0) y la
// ficha de habilidad de 04 · 36 §3.1: un struct plano por arma, sin lógica.
// ---------------------------------------------------------------------------

#macro ARMA_MAX_NIVEL 8

global.armas_def = {
    latigo : {
        nombre            : "Látigo",
        cadencia_frames   : 50,
        dano_base         : 8,
        alcance           : 90,
        objetivo          : "cercano",
        evoluciona_con    : "guante_vacio",
        evolucion         : "guadana_sangrienta"
    },
    orbe_magico : {
        nombre            : "Orbe mágico",
        cadencia_frames   : 90,
        dano_base         : 12,
        alcance           : 220,
        objetivo          : "orbital",
        evoluciona_con    : "espejo_vacio",
        evolucion         : "orbe_prisma"
    }
};

/// @func ArmaEstado(_id_arma)
/// @desc Una instancia de un arma del catálogo, equipada por el jugador con su
///       propio nivel y temporizador. No confundir con ArmaDef: esto es el
///       ESTADO, el catálogo es el DATO (mismo principio que 04 · 36 §1.2).
function ArmaEstado(_id_arma) constructor
{
    id_arma      = _id_arma;
    def          = global.armas_def[$ _id_arma];
    nivel        = 1;
    temporizador = 0;

    static estadisticas = function()
    {
        return {
            dano     : def.dano_base * (1 + 0.35 * (nivel - 1)),
            cadencia : max(8, def.cadencia_frames - 4 * (nivel - 1)),
        };
    };

    static subir_nivel = function()
    {
        nivel = min(nivel + 1, ARMA_MAX_NIVEL);
    };

    /// @desc Se llama una vez por frame desde el Step del jugador. El arma NO
    ///       espera ningún input: dispara sola cuando el temporizador llega a 0.
    static actualizar = function(_x, _y)
    {
        var _st = estadisticas();
        temporizador -= 1;
        if (temporizador <= 0)
        {
            temporizador = _st.cadencia;
            disparar(_x, _y, _st);
        }
    };

    static disparar = function(_x, _y, _st)
    {
        var _obj = instance_nearest(_x, _y, obj_enemigo);
        if (!instance_exists(_obj)) return;

        var _dir = point_direction(_x, _y, _obj.x, _obj.y);
        var _p   = global.pool_proyectiles_jugador.get_at(_x, _y);
        if (_p == noone) return;

        _p.direction = _dir;
        _p.speed     = 10;
        _p.dano      = _st.dano;
    };
}
```

#### 1.5.1 · Director de oleadas por nivel (curva geométrica)

```gml
// ---------------------------------------------------------------------------
// obj_director_oleadas — variante de curva por nivel (§1.4.2, opción B)
// ---------------------------------------------------------------------------

/// Create
nivel               = 1;
xp                  = 0;
xp_meta             = 10;
spawn_cooldown_base = 60;   // fotogramas entre spawns, baja con el nivel
enemigo_vida_bonus  = 1;    // multiplicador, sube con el nivel
spawn_timer         = spawn_cooldown_base;

/// Step
if (!global.pausado)
{
    spawn_timer -= 1;
    if (spawn_timer <= 0)
    {
        spawn_timer = spawn_cooldown_base;
        spawn_enemigo_fuera_de_camara(elegir_tipo_enemigo(nivel));
    }
}

// Al recibir XP (llamado desde donde muere un enemigo, no aquí):
// xp += cantidad; if (xp >= xp_meta) { avanzar_oleada(); }

/// @func avanzar_oleada()
/// @desc Ecualiza los tres parámetros de dificultad en un único instante, igual
///       que next_wave() de la Survivor Game Template oficial (§1.4.2).
function avanzar_oleada()
{
    xp -= xp_meta;
    xp_meta             = floor(xp_meta * 1.2);   // curva de coste geométrica, 13 · 01 §4.4
    spawn_cooldown_base = max(10, spawn_cooldown_base - 3);
    enemigo_vida_bonus *= 1.25;
    nivel += 1;

    mostrar_pantalla_mejora(get_opciones_mejora());
}

/// @func elegir_tipo_enemigo(_nivel)
/// @desc Variedad progresiva: más tipos de enemigo cuantas más oleadas pasan,
///       no solo más vida en los mismos (§1.4.2).
function elegir_tipo_enemigo(_nivel)
{
    if (_nivel <= 2) return obj_enemigo_basico;
    if (_nivel <= 4) return choose(obj_enemigo_basico, obj_enemigo_rapido);
    return choose(obj_enemigo_basico, obj_enemigo_rapido, obj_enemigo_tanque);
}
```

#### 1.5.2 · Elegir 1 de 3 mejoras, ponderado

```gml
// ---------------------------------------------------------------------------
// scr_mejoras
// ---------------------------------------------------------------------------

/// @func get_opciones_mejora()
/// @desc Reúne toda mejora disponible AHORA MISMO (arma no equipada primero) y
///       devuelve 3 al azar, sin repetir. Usa el generador global si la
///       reproducibilidad no importa; usa una instancia propia de RNG (04 · 05
///       §5.0) si la partida necesita semilla (carreras diarias, por ejemplo).
function get_opciones_mejora()
{
    var _candidatas = [];

    // 1. Armas no equipadas: prioridad, van todas a la bolsa igual que las demás
    //    (la ponderación real vive en cuántas veces se repite cada una — ver
    //    array_push más abajo, no en un peso separado).
    var _nombres_armas = struct_get_names(global.armas_def);
    for (var _i = 0; _i < array_length(_nombres_armas); _i++)
    {
        var _id = _nombres_armas[_i];
        if (!arma_equipada(_id))
        {
            array_push(_candidatas, { tipo: "desbloquear", id_arma: _id });
        }
        else
        {
            var _estado = obj_jugador.armas[$ _id];
            if (_estado.nivel < ARMA_MAX_NIVEL)
            {
                array_push(_candidatas, { tipo: "subir_nivel", id_arma: _id });
            }
        }
    }

    // 2. Barajar y tomar las 3 primeras — array_shuffle_ext no reutiliza el
    //    array (lo modifica en el sitio, verificado con buscar.py).
    array_shuffle_ext(_candidatas);
    var _n = min(3, array_length(_candidatas));
    var _resultado = [];
    for (var _j = 0; _j < _n; _j++) { array_push(_resultado, _candidatas[_j]); }
    return _resultado;
}

/// @func aplicar_mejora(_opcion)
function aplicar_mejora(_opcion)
{
    if (_opcion.tipo == "desbloquear")
    {
        obj_jugador.armas[$ _opcion.id_arma] = new ArmaEstado(_opcion.id_arma);
    }
    else
    {
        obj_jugador.armas[$ _opcion.id_arma].subir_nivel();
        if (puede_evolucionar(obj_jugador.armas[$ _opcion.id_arma], obj_jugador.pasivas))
        {
            evolucionar_arma(_opcion.id_arma);
        }
    }
}
```

#### 1.5.3 · Enemigo pooled con imán de XP al morir

```gml
// ---------------------------------------------------------------------------
// obj_enemigo — pensado para vivir dentro de una Pool (§1.4.5)
// ---------------------------------------------------------------------------

/// Create — se ejecuta UNA vez, al pre-crear el pool, no en cada spawn
hitpoints_max = 0;   // lo fija get_at() al reciclar, no aquí
hitpoints     = 0;
depth         = 0;

/// Método de reinicio, llamado por Pool.get_at() vía reset_vars (06/scr_pool.gml)
/// pool_enemigos.set_reset_vars({ hitpoints_max: 10, hitpoints: 10 });

/// Step
if (!instance_exists(obj_jugador)) exit;

direction = point_direction(x, y, obj_jugador.x, obj_jugador.y);
speed     = velocidad_base;
depth     = -y;   // orden top-down, igual que 04 · 02

/// Al recibir daño (llamado desde el proyectil, usando 04 · 32):
// hitpoints -= dano_resolver(_dano_bruto, DanoTipo.FISICO, 0, undefined);
// if (hitpoints <= 0) { morir(); }

function morir()
{
    var _xp = global.pool_recogibles_xp.get_at(x, y);
    if (_xp != noone) { _xp.valor = valor_xp; _xp.activo = true; }

    global.pool_enemigos.release(id);   // NUNCA instance_destroy() — §1.4.5
}
```

### 1.6 · Errores clásicos y cómo evitarlos

- **`instance_destroy()` sobre un enemigo o proyectil en vez de `pool.release()`.** El primer
  minuto de partida no lo nota nadie; al minuto 15, con miles de creaciones/destrucciones
  acumuladas, el framerate se derrumba de golpe. Es exactamente el error que
  [`scr_pool.gml`](<../06 - Assets y Scripts/scr_pool.gml>) documenta en su cabecera.
- **Ofrecer 3 opciones sin comprobar qué armas ya están al máximo.** Si el generador de `§1.5.2`
  no filtra armas en `ARMA_MAX_NIVEL`, el jugador ve "subir nivel" de un arma que ya no puede
  subir, y la elección se siente rota.
- **Curva de dificultad que sube en línea recta en vez de geométrica.** Un `enemigo_vida_bonus
  += 0.25` cada oleada, en vez de `*= 1.25`, hace que las primeras oleadas se sientan iguales y
  las últimas insultantemente fáciles — la razón por la que `next_wave()` de la plantilla
  oficial multiplica, no suma (`§1.4.2`, `13 · 01 §4.4`).
- **Radio de imán de XP comprobado con `point_distance` sin más, para cientos de recogibles a la
  vez.** Cada llamada calcula una raíz cuadrada; comparar `sqr(dx) + sqr(dy) < sqr(_radio)` evita
  la raíz en el caso común (solo hace falta la distancia real cuando ya se decidió mover el
  objeto, no para la comprobación de "¿está dentro?").
- **Confundir esto con `04 · 09` porque los dos usan la palabra "supervivencia".** `04 · 09` es
  gestionar necesidades sin amenaza activa (hambre, sed, frío); este documento es sobrevivir a
  una horda que ataca sin parar. Si tu diseño mezcla los dos (hambre + horda), documenta cuál es
  el sistema principal para no acabar con dos economías de "vida" que se pisan.

---

## 2 · Autobattler

### 2.1 · Visión general

Un autobattler (o *auto-battler*, popularizado como género independiente por *Dota Auto Chess*
y comercializado por Riot Games como *Teamfight Tactics*) le pide al jugador **preparar** un
equipo y luego mirar cómo lucha solo. La habilidad del jugador está en la fase de preparación
—qué comprar, dónde colocarlo, cuándo gastar oro y cuándo ahorrarlo— nunca en ejecutar el
combate en tiempo real. *Super Auto Pets* (Team Wood Games), un autobattler más ligero y sin
tablero espacial, lo resume en su propia ficha de Steam: *"Build a team of cute pets with
unique abilities. Battle against other players"*, con partidas que terminan al llegar a *"10
wins before losing all your hearts"* (<https://store.steampowered.com/app/1714040/Super_Auto_Pets/>,
consultado 2026-09-06) — la estructura de vidas/corazones en vez de HP único es una variante
habitual del género frente al HP compartido de *Teamfight Tactics*.

**Lo que define al género, frente a lo que ya cubre la biblioteca:**

- **El combate se resuelve sin input del jugador**, a diferencia de `04 · 13` (Estrategia y
  gestión), donde el jugador da órdenes en tiempo real durante el combate. Aquí el combate es
  una simulación que corre sola una vez empieza (`§2.4.5`).
- **La tienda con *reroll*** es el sistema nuevo que `04 · 13 §1` ni menciona: comprar no es
  solo "gastar oro en una unidad", es decidir entre gastar en unidades nuevas, en subir el nivel
  de tienda, o en ahorrar para interés (`§2.4.2`, `§2.4.3`).
- **Las sinergias por tipo/clase** son la capa de diseño que convierte "montón de unidades" en
  "equipo": una unidad sola vale poco; tres del mismo tipo activan un bono que cambia el
  combate entero (`§2.4.4`).

**Referencias:** *Dota Auto Chess* (Drodo Studio, 2019, el origen del género como mod),
*Teamfight Tactics* (Riot Games, 2019), *Super Auto Pets* (Team Wood Games, 2021, sin tablero:
solo una fila lineal de mascotas). GameMaker no publica plantilla oficial de este género — a
diferencia de *bullet heaven*, aquí no hay un punto de partida oficial que citar; `04 · 13 §5`
ya trae selección múltiple, grid y UI Layers que este bloque reutiliza para el tablero.

### 2.2 · Arquitectura recomendada

```
obj_tablero          Grid de casillas donde se colocan las unidades del jugador
obj_unidad           Una unidad colocada (jugador o rival); reutilizable con struct de datos
obj_tienda           5 casillas de compra, con reroll y subida de nivel de tienda
obj_banca            Gestiona el oro: ingreso por ronda, interés, gasto
obj_director_rondas   Alterna preparación ↔ combate, y empareja al jugador contra un rival
```

**Structs (mismo patrón de catálogo que `§1.5.0`):**

```
UnidadDef      catálogo estático: coste, tipo(s)/sinergia, estadísticas base, habilidad
UnidadEstado   una copia de UnidadDef colocada en el tablero, con estrella (1★/2★/3★) y vida actual
SinergiaDef    catálogo de bonos: cuántas unidades del mismo tipo activan qué efecto
```

### 2.3 · El bucle central

```
┌─ Cada ronda ──────────────────────────────────────────────────┐
│ 1. FASE DE PREPARACIÓN (temporizador visible, 20-30 s)         │
│    - Banca: aplicar ingreso de ronda + interés (§2.4.3)         │
│    - Tienda: refrescar 5 unidades al azar (gratis, una vez)     │
│    - Jugador: comprar, colocar en el tablero, vender, reroll,   │
│      subir nivel de tienda — todo con el oro disponible         │
│ 2. FIN DE PREPARACIÓN → congelar el tablero: snapshot inmutable │
│ 3. FASE DE COMBATE                                              │
│    - Emparejar contra un rival (otro jugador, o un enjambre     │
│      neutral en rondas tempranas)                                │
│    - Simular el combate entero con RNG de semilla fija (§2.4.5) │
│    - Aplicar resultado: daño al perdedor, oro de bonificación    │
│ 4. Volver a 1, con la dificultad/nivel de rival escalado         │
└─────────────────────────────────────────────────────────────────┘
```

La pieza que no existe en ningún otro género de esta biblioteca es el **paso 2**: el tablero se
congela antes de simular, así que el combate puede correr más rápido que tiempo real (o
mostrarse a velocidad normal solo por espectáculo) sin que el jugador pueda interferir a mitad.

### 2.4 · Sistemas clave

#### 2.4.1 · Tablero: colocación en grid

Un grid cuadrado o hexagonal donde el jugador coloca sus unidades en su mitad, y el motor coloca
las del rival (o las copia en espejo) en la otra. Representarlo como **array de arrays**, no
`ds_grid` (la convención de la biblioteca es evitar `ds_*` salvo que aporten algo que un array no
dé — aquí no lo dan). El array 2D tiene una trampa real del propio manual de GameMaker:

```gml
/// @func tablero_nuevo(_columnas, _filas)
/// @desc ⚠️ NO uses array_create(_filas, array_create(_columnas, noone)): el
///       manual de array_create es explícito — si el valor de relleno es un
///       array o struct, TODAS las filas comparten la MISMA referencia, y
///       escribir en una casilla de la fila 0 cambiaría la fila 3 también.
function tablero_nuevo(_columnas, _filas)
{
    var _tablero = array_create(_filas);
    for (var _f = 0; _f < _filas; _f++)
    {
        _tablero[_f] = array_create(_columnas, noone);   // un array NUEVO por fila
    }
    return _tablero;
}

/// @func tablero_colocar(_tablero, _col, _fila, _unidad_estado)
function tablero_colocar(_tablero, _col, _fila, _unidad_estado)
{
    if (_tablero[_fila][_col] != noone) return false;   // casilla ocupada
    _tablero[_fila][_col] = _unidad_estado;
    return true;
}
```

#### 2.4.2 · Tienda con *reroll*: pool compartido y probabilidades por tier

Todas las unidades que existen en la partida viven en un **pool compartido** entre todos los
jugadores: si compras la única copia que queda de una unidad rara, a nadie más le puede salir
hasta que alguien la venda. Esto es lo que hace que la tienda sea una decisión de *timing*, no
solo de gasto. El *reroll* refresca las 5 casillas con un sorteo nuevo del pool, con un coste
fijo en oro (convención del género: 2 de oro por *reroll*, sin límite de usos por ronda):

```gml
/// @func UnidadDef, en un catálogo global por "tier" (coste)
global.unidades_def = {
    tier_1 : ["explorador", "curandero", "arquero"],
    tier_2 : ["caballero", "hechicero"],
    tier_3 : ["campeon", "invocador"],
};

// Probabilidad de que cada tier aparezca en la tienda, según el NIVEL de tienda
// del jugador (no el nivel del personaje: subir el nivel de tienda es una
// compra más, en competencia directa con comprar unidades — §2.4.3).
global.probabilidad_por_nivel_tienda = [
    [1.00, 0.00, 0.00],   // nivel 1: solo tier 1
    [0.75, 0.25, 0.00],   // nivel 2
    [0.55, 0.35, 0.10],   // nivel 3
    [0.35, 0.40, 0.25],   // nivel 4
];

/// @func tienda_refrescar(_nivel_tienda)
/// @desc Sortea 5 unidades del pool compartido según la tabla de probabilidad
///       por tier. Usa random_range/choose (04 · 05, catálogo de 13 · 13 §5.1);
///       si la partida necesita revancha exacta (mismo sorteo en un replay),
///       usa una instancia de RNG (04 · 05 §5.0) en vez del generador global.
function tienda_refrescar(_nivel_tienda)
{
    var _probs = global.probabilidad_por_nivel_tienda[clamp(_nivel_tienda - 1, 0, 3)];
    var _resultado = [];

    repeat (5)
    {
        var _r = random(1);
        var _acumulado = 0;
        var _tier_elegido = 1;
        for (var _t = 0; _t < array_length(_probs); _t++)
        {
            _acumulado += _probs[_t];
            if (_r <= _acumulado) { _tier_elegido = _t + 1; break; }
        }

        var _pool_tier = global.unidades_def[$ "tier_" + string(_tier_elegido)];
        array_push(_resultado, _pool_tier[irandom(array_length(_pool_tier) - 1)]);
    }

    return _resultado;
}

/// @func tienda_reroll(_banca, _nivel_tienda)
#macro COSTE_REROLL 2
function tienda_reroll(_banca, _nivel_tienda)
{
    if (_banca.oro < COSTE_REROLL) return undefined;
    _banca.oro -= COSTE_REROLL;
    return tienda_refrescar(_nivel_tienda);
}
```

#### 2.4.3 · Economía: oro por ronda e interés

El oro tiene una **fuente** fija por ronda (independiente de si ganas o pierdes: el género
premia jugar, no solo ganar) y un **interés** que recompensa ahorrar, con tramos — la misma
"curva de coste geométrica invertida": cuanto más oro guardas, más rápido crece, hasta un techo
que evita que la partida se decida solo por quién ahorró más al principio (bola de nieve
positiva sin freno, `13 · 01 §4.2`):

```gml
// ---------------------------------------------------------------------------
// scr_banca — economía de ronda (§0.4, aplicando 13 · 01 §4)
// ---------------------------------------------------------------------------

#macro INGRESO_BASE_POR_RONDA 5
#macro INTERES_TRAMO_ORO      10   // cada 10 de oro ahorrado dan +1 de interés
#macro INTERES_MAXIMO         5    // techo: el sumidero de la bola de nieve (13 · 01 §4.2)

/// @func banca_ingreso_de_ronda(_banca, _gano_combate, _racha)
/// @desc Ingreso = base + interés + bonus de racha (ganar o perder varias
///       veces seguidas también da oro, para no castigar doblemente al que
///       ya va perdiendo).
function banca_ingreso_de_ronda(_banca, _gano_combate, _racha)
{
    var _interes = min(floor(_banca.oro / INTERES_TRAMO_ORO), INTERES_MAXIMO);
    var _bonus_racha = (_racha >= 3) ? min(_racha - 2, 3) : 0;
    var _ingreso = INGRESO_BASE_POR_RONDA + _interes + _bonus_racha + (_gano_combate ? 1 : 0);

    _banca.oro += _ingreso;
    return _ingreso;
}
```

⚠️ Los tramos exactos (10 de oro por punto de interés, techo de 5) son una **convención muy
extendida en el género** — es el patrón que hizo popular *Teamfight Tactics*, pero los valores
concretos cambian entre parches y entre juegos; no hay una fuente primaria única y estable que
fije "el número correcto". Trátalos como punto de partida y ajústalos con la simulación de
`13 · 19` (cuando exista) o con *playtesting* real, igual que cualquier otra curva de balance de
`13 · 01 §4.4`.

#### 2.4.4 · Sinergias por tipo

Cada unidad pertenece a uno o más tipos (`guerrero`, `mago`, `bestia`...) y una sinergia se
activa cuando el tablero tiene un número mínimo de unidades del mismo tipo — el motor recorre el
tablero una vez por cambio (no cada frame) y recalcula qué sinergias están activas:

```gml
global.sinergias_def = {
    guerrero : { umbrales: [2, 4, 6], efecto: "armadura_extra" },
    mago     : { umbrales: [2, 4],    efecto: "dano_habilidad_extra" },
};

/// @func calcular_sinergias_activas(_tablero)
/// @desc Se llama SOLO al colocar/quitar una unidad, no en el Step — recorrer
///       el tablero entero cada frame no aporta nada si no cambió nada.
function calcular_sinergias_activas(_tablero)
{
    var _conteo = {};   // { tipo: cuántas unidades de ese tipo hay colocadas }

    for (var _f = 0; _f < array_length(_tablero); _f++)
    {
        for (var _c = 0; _c < array_length(_tablero[_f]); _c++)
        {
            var _unidad = _tablero[_f][_c];
            if (_unidad == noone) continue;

            for (var _t = 0; _t < array_length(_unidad.tipos); _t++)
            {
                var _tipo = _unidad.tipos[_t];
                var _actual = variable_struct_exists(_conteo, _tipo) ? _conteo[$ _tipo] : 0;
                _conteo[$ _tipo] = _actual + 1;
            }
        }
    }

    var _activas = {};
    var _tipos_def = struct_get_names(global.sinergias_def);
    for (var _i = 0; _i < array_length(_tipos_def); _i++)
    {
        var _tipo = _tipos_def[_i];
        var _cuantas = variable_struct_exists(_conteo, _tipo) ? _conteo[$ _tipo] : 0;
        var _umbrales = global.sinergias_def[$ _tipo].umbrales;

        var _nivel_activo = 0;
        for (var _u = 0; _u < array_length(_umbrales); _u++)
        {
            if (_cuantas >= _umbrales[_u]) _nivel_activo = _u + 1;
        }
        if (_nivel_activo > 0) _activas[$ _tipo] = _nivel_activo;
    }

    return _activas;
}
```

#### 2.4.5 · Combate resuelto solo: simulación determinista con semilla

El combate no se dibuja "de verdad" mientras se decide: primero se **simula por completo** con
una semilla fija (para que el resultado sea reproducible si hace falta reenviarlo, depurarlo o
mostrarlo a espectadores frame por frame más tarde), y solo después se anima. Reutiliza el
`RNG()` de
[04 · 05 §5.0](./05%20-%20Roguelike%20y%20generación%20procedural.md#50-generador-aleatorio-propio-independiente-del-global) —
no lo redefinas aquí:

```gml
// ---------------------------------------------------------------------------
// scr_combate_auto
// ---------------------------------------------------------------------------

/// @func equipos_simular_combate(_equipo_a, _equipo_b, _semilla)
/// @desc Corre el combate entero de una vez, sin dibujar nada. _equipo_a y
///       _equipo_b son copias INDEPENDIENTES de las unidades del tablero
///       (variable_clone, para no mutar el tablero real mientras se simula).
///       Nombre específico (no `simular_combate` a secas): `13 · 21` ya usa ese
///       nombre para su simulación de TTK arma-contra-enemigo, con otra aridad.
/// @returns {Struct} { gano_a: Bool, log: Array, sobrevivientes_a: Array }
function equipos_simular_combate(_equipo_a, _equipo_b, _semilla)
{
    var _rng = new RNG(_semilla);   // constructor completo en 04 · 05 §5.0
    var _log = [];
    var _tick = 0;

    while (equipo_tiene_vivos(_equipo_a) && equipo_tiene_vivos(_equipo_b) && _tick < 600)
    {
        combate_tick(_equipo_a, _equipo_b, _rng, _log);
        combate_tick(_equipo_b, _equipo_a, _rng, _log);
        _tick += 1;
    }

    return {
        gano_a            : equipo_tiene_vivos(_equipo_a),
        log               : _log,
        sobrevivientes_a  : equipo_vivos(_equipo_a),
    };
}

/// @desc Un tick: cada unidad viva de _atacantes golpea a un objetivo de
///       _defensores, elegido con el RNG de semilla (no con random() global,
///       o dos simulaciones de la misma ronda darían resultados distintos).
function combate_tick(_atacantes, _defensores, _rng, _log)
{
    for (var _i = 0; _i < array_length(_atacantes); _i++)
    {
        var _u = _atacantes[_i];
        if (_u.vida <= 0) continue;

        var _vivos_def = equipo_vivos(_defensores);
        if (array_length(_vivos_def) == 0) return;

        var _objetivo = _vivos_def[_rng.int(array_length(_vivos_def) - 1)];
        var _dano = dano_resolver(_u.ataque, _u.tipo_dano, 0, _objetivo);   // 04 · 32 §5.1
        _objetivo.vida -= _dano;
        array_push(_log, { atacante: _u.id, objetivo: _objetivo.id, dano: _dano });
    }
}
```

⚠️ `dano_resolver()` espera el struct `combate` de `04 · 32` como cuarto argumento (armadura,
resistencias, escudo); aquí se pasa `_objetivo` como abreviatura — si tu `UnidadEstado` no tiene
exactamente los mismos campos que `EstadoCombate`, envuélvelo o adáptalo antes de llamarlo. No
reimplementes el pipeline de daño: `04 · 32` ya resuelve tipo, armadura y escudo.

### 2.5 · Errores clásicos y cómo evitarlos

- **Compartir el array de una fila del tablero entre casillas** (`§2.4.1`): el `array_create`
  con un array/struct de relleno crea una única referencia compartida; el manual oficial lo
  avisa explícitamente y `array_create_ext` es la alternativa cuando cada elemento necesita ser
  único.
- **Simular el combate con `random()` global en vez de una `RNG` con semilla.** Sin semilla, no
  puedes reproducir un combate para depurar un caso raro ("¿por qué perdí con un equipo mejor?"),
  ni ofrecer un *replay* fiel.
- **Recalcular sinergias en el `Step`.** El tablero solo cambia cuando el jugador compra, vende o
  mueve una unidad — recalcular en cada frame malgasta ciclos en un valor que no cambió; hazlo
  en el evento de colocar/quitar, como muestra `§2.4.4`.
- **Interés sin techo.** Un interés que crece sin límite convierte la partida en "quien llegó
  antes a ahorrar mucho gana", eliminando cualquier decisión de mitad de partida — exactamente
  el fallo de realimentación positiva sin freno de `13 · 01 §4.2`.
- **Tienda con pool infinito en vez de compartido.** Si cada jugador tiene su propio pool de
  unidades sin relación con los demás, desaparece la tensión de "alguien más se está llevando
  las copias que yo necesito", que es gran parte de la lectura táctica del género.

---

## 3 · Deckbuilder

### 3.1 · Visión general

Un *deckbuilder* de un jugador (el subgénero que popularizó *Slay the Spire*, MegaCrit, 2019) le
pide al jugador **construir un mazo durante la partida**, combate a combate, en vez de traerlo ya
hecho. La propia ficha de Steam del juego lo resume así: *"We fused card games and roguelikes
together to make the best single player deckbuilder we could"*, con **Dynamic Deck Building**
como característica destacada: *"Choose your cards wisely! Discover hundreds of cards to add to
your deck with each attempt at climbing the Spire"*
(<https://store.steampowered.com/app/646570/Slay_the_Spire/>, consultado 2026-09-06). Esa frase
es la clave de diseño: el mazo no es un recurso fijo, es la decisión central de toda la partida.

**Lo que define al género, frente a lo que ya cubre la biblioteca:**

- **El estado de "qué cartas tengo en la mano ahora mismo" es efímero y cíclico** (mano → jugada
  → descarte → de vuelta al mazo cuando se agota), a diferencia del inventario persistente de
  `04 · 04` (RPG), donde un objeto no desaparece al usarlo salvo que sea consumible.
- **Los efectos de las cartas son datos, no ramas de código**, igual que las habilidades de
  `04 · 36 §1.2` o los ataques de `04 · 30 §2.3` — pero aquí cada partida mezcla decenas de
  cartas con datos distintos, así que el intérprete de efectos tiene que ser más genérico que en
  esos dos documentos.
- **La energía/maná por turno es el recurso que limita cuántas cartas se juegan**, no el coste
  de cada carta por separado — la curva de maná (`§3.4.4`) es la pieza de balance que decide si
  el mazo se siente "rápido" o "lento".

**Referencias:** *Slay the Spire* (MegaCrit, 2019, el que fijó el vocabulario del subgénero de
un jugador: reliquia, ascensión, energía), *Monster Train* (Shiny Shoe, 2020, dos carriles de
combate en vez de uno), *Balatro* (LocalThunk, 2024, el mismo esqueleto aplicado al póker en vez
de al combate). GameMaker publica una **Card Game Template** oficial, pero es de tipo solitario
—*"Build a Solitaire style Card game"* (API oficial, verificado 2026-09-06)—: sirve como punto de
partida para arrastrar cartas y reglas por pilas, pero no trae combate, maná ni recompensas entre
partidas; no es un punto de partida para un *deckbuilder* de combate como el de este bloque.

### 3.2 · Arquitectura recomendada

```
obj_combate          Controla el turno, la energía disponible y el estado de la mano
obj_carta_ui         Representación visual de una carta en la mano (arrastrable)
obj_enemigo_combate   Uno o más enemigos con intención visible (qué van a hacer este turno)
obj_mapa_run          Nodos del mapa entre combates: elegir ruta, tienda, evento, jefe
```

**Structs (mismo patrón de catálogo que `§1.5.0` y `§2.2`):**

```
CartaDef       catálogo estático: coste de energía, tipo, efecto(s) por datos, rareza
CartaInstancia una COPIA de CartaDef en el mazo del jugador (variable_clone — §3.4.1),
               con su propio estado de "mejorada" si el género lo permite
Mazo           las cuatro pilas (mazo, mano, descarte, exilio) y sus transiciones
```

`array_clone_barajado()` (§3.4.2) y el `Create` PvP (§3.6) leen `global.semilla_combate`: fíjala
al entrar en el combate, ANTES de barajar el mazo —

```gml
/// obj_combate · Create (un jugador; en PvP la fija el servidor antes de crear las dos bandas)
global.semilla_combate = irandom(999999);   // guárdala si el run necesita ser reproducible
```

### 3.3 · El bucle central

```
┌─ Cada combate ─────────────────────────────────────────────────┐
│ 1. Barajar el mazo completo (Fisher-Yates con semilla, §3.4.2)   │
│ 2. INICIO DE TURNO:                                              │
│    - Restaurar energía al máximo (no se acumula entre turnos)    │
│    - Robar N cartas del mazo a la mano (§3.4.1)                  │
│    - Los enemigos revelan su intención (qué van a hacer)         │
│ 3. TURNO DEL JUGADOR (sin límite de tiempo, salvo que el diseño   │
│    lo añada):                                                    │
│    - Jugar cartas mientras haya energía y cartas jugables        │
│    - Cada carta jugada: gasta energía, resuelve su efecto por     │
│      datos (§3.4.3), pasa a descarte (o exilio si dice "exile")  │
│ 4. FIN DE TURNO: cartas no jugadas → descarte; enemigos ejecutan  │
│    su intención revelada                                          │
│ 5. Volver a 2, hasta que un bando llegue a 0 de vida               │
│ 6. Al ganar: recompensa — elegir 1 de 3 cartas, y a veces oro      │
│    o una reliquia (§3.4.5) — vuelve al mapa entre combates         │
└────────────────────────────────────────────────────────────────┘
```

### 3.4 · Sistemas clave

#### 3.4.1 · Las cuatro pilas y sus transiciones

Un mazo de *deckbuilder* de combate no es un solo array: son **cuatro pilas** con reglas de
transición fijas, y casi todos los bugs del género salen de mover una carta a la pila
equivocada:

| Pila | Qué contiene | De dónde vienen las cartas | A dónde van |
|---|---|---|---|
| **Mazo** (*draw pile*) | Cartas por robar, boca abajo | Se rellena SOLO reciclando el descarte cuando se vacía | Mano (al robar) |
| **Mano** (*hand*) | Cartas disponibles este turno | Mazo (robo) | Descarte (al jugar o al pasar turno) o exilio (efecto especial) |
| **Descarte** (*discard pile*) | Cartas ya usadas o no jugadas | Mano | Mazo (cuando el mazo se vacía: se baraja el descarte entero) |
| **Exilio** (*exhaust pile*) | Cartas fuera de la partida hasta el próximo combate | Mano, solo con efecto explícito | Ninguna (vuelven al mazo entre combates, no dentro de uno) |

```gml
// ---------------------------------------------------------------------------
// scr_mazo — las cuatro pilas, como arrays de CartaInstancia
// ---------------------------------------------------------------------------

/// @func Mazo(_cartas_iniciales)
function Mazo(_cartas_iniciales) constructor
{
    robo      = array_clone_barajado(_cartas_iniciales);   // §3.4.2
    mano      = [];
    descarte  = [];
    exilio    = [];

    /// @desc Roba _n cartas del mazo a la mano. Si el mazo se vacía a mitad,
    ///       baraja el descarte y lo convierte en el nuevo mazo — SIN perder
    ///       las cartas que ya se robaron en esta misma llamada.
    static robar = function(_n, _rng)
    {
        repeat (_n)
        {
            if (array_length(robo) == 0)
            {
                if (array_length(descarte) == 0) return;   // no queda nada que robar
                robo = descarte;
                descarte = [];
                _rng.shuffle(robo);
            }
            array_push(mano, array_pop(robo));
        }
    };

    /// @desc Mueve una carta de la mano al descarte (o exilio) por índice.
    static jugar = function(_indice_mano, _a_exilio = false)
    {
        var _carta = mano[_indice_mano];
        array_delete(mano, _indice_mano, 1);
        array_push(_a_exilio ? exilio : descarte, _carta);
        return _carta;
    };

    /// @desc Fin de turno: toda la mano restante va al descarte.
    static descartar_mano = function()
    {
        for (var _i = 0; _i < array_length(mano); _i++) { array_push(descarte, mano[_i]); }
        mano = [];
    };
}
```

#### 3.4.2 · Robar y barajar con semilla

El barajado usa el mismo `RNG()` de
[04 · 05 §5.0](./05%20-%20Roguelike%20y%20generación%20procedural.md#50-generador-aleatorio-propio-independiente-del-global)
— **no** el `random()` global, por la misma razón de `13 · 01 §5.2`: si el combate usa el mismo
flujo aleatorio que la generación del mapa entre combates, cambiar de estrategia de combate
altera qué nodo de mapa toca después, y un *seed run* (compartir semilla entre jugadores, tan
habitual en el género para las carreras diarias) deja de ser justo.

```gml
/// @func array_clone_barajado(_cartas_def)
/// @desc Convierte un array de CartaDef (catálogo, compartido) en un array de
///       CartaInstancia (copias independientes, cada una con su propio estado
///       de "mejorada") y lo baraja. variable_clone evita el mismo problema de
///       referencia compartida que array_create con un struct de relleno.
function array_clone_barajado(_cartas_def)
{
    var _mazo = [];
    for (var _i = 0; _i < array_length(_cartas_def); _i++)
    {
        array_push(_mazo, variable_clone(_cartas_def[_i]));   // copia única, no referencia
    }

    var _rng = new RNG(global.semilla_combate);   // constructor en 04 · 05 §5.0
    _rng.shuffle(_mazo);
    return _mazo;
}
```

Si además necesitas evitar que **la misma carta de recompensa** se repita demasiado seguido
entre combates (una queja habitual del género cuando el RNG puro da tres veces la misma carta de
seguido), la **bolsa aleatoria** de
[13 · 13 §5.5](<../13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md#55--bolsa-aleatoria-shuffle-bag>)
es la herramienta correcta para el generador de recompensas de `§3.4.5` — no la reimplementes
aquí, ese documento ya trae el código completo.

#### 3.4.3 · Efectos de carta por datos

Cada carta es un struct con una lista de efectos, no una función escrita a mano por carta — el
mismo principio que `04 · 36 §1.2` aplica a las habilidades:

```gml
global.cartas_def = {
    golpe : {
        nombre  : "Golpe",
        coste   : 1,
        tipo    : "ataque",
        rareza  : "comun",
        efectos : [ { accion: "dano", cantidad: 6, objetivo: "enemigo_seleccionado" } ]
    },
    defensa : {
        nombre  : "Defensa",
        coste   : 1,
        tipo    : "habilidad",
        rareza  : "comun",
        efectos : [ { accion: "bloqueo", cantidad: 5, objetivo: "uno_mismo" } ]
    },
    torrente : {
        nombre  : "Torrente",
        coste   : 2,
        tipo    : "ataque",
        rareza  : "rara",
        efectos : [
            { accion: "dano",  cantidad: 4, objetivo: "todos_enemigos" },
            { accion: "robar", cantidad: 1, objetivo: "uno_mismo" }
        ]
    },
};

/// @func resolver_efecto(_efecto, _origen, _objetivo_seleccionado, _mazo)
/// @desc Intérprete genérico: un `switch` por tipo de acción, no una función
///       por carta. Añadir una carta nueva casi nunca toca este código.
function resolver_efecto(_efecto, _origen, _objetivo_seleccionado, _mazo)
{
    switch (_efecto.accion)
    {
        case "dano":
            var _objetivos = (_efecto.objetivo == "todos_enemigos")
                ? obj_combate.enemigos_vivos()
                : [_objetivo_seleccionado];
            for (var _i = 0; _i < array_length(_objetivos); _i++)
            {
                var _dano = dano_resolver(_efecto.cantidad, DanoTipo.FISICO, 0, _objetivos[_i]); // 04 · 32
                _objetivos[_i].vida -= _dano;
            }
            break;

        case "bloqueo":
            _origen.bloqueo += _efecto.cantidad;
            break;

        case "robar":
            _mazo.robar(_efecto.cantidad, obj_combate.rng);
            break;
    }
}

/// @func jugar_carta(_indice_mano, _objetivo_seleccionado)
function jugar_carta(_indice_mano, _objetivo_seleccionado)
{
    var _carta = obj_combate.mazo.mano[_indice_mano];
    if (obj_combate.energia < _carta.coste) return false;   // no alcanza

    obj_combate.energia -= _carta.coste;
    for (var _i = 0; _i < array_length(_carta.efectos); _i++)
    {
        resolver_efecto(_carta.efectos[_i], obj_combate.jugador, _objetivo_seleccionado, obj_combate.mazo);
    }

    obj_combate.mazo.jugar(_indice_mano, variable_struct_exists(_carta, "exilia") && _carta.exilia);
    return true;
}
```

#### 3.4.4 · Curva de maná

La energía por turno es constante durante todo el combate (a diferencia de la vida, que sube y
baja) pero **crece entre actos** de la partida — más energía disponible más adelante compensa
que los enemigos también sean más duros. La curva de coste de las cartas del mazo debe seguir a
la energía disponible, no al revés: si la energía por turno es 3 y la mitad del mazo cuesta 3 o
más, el jugador solo puede jugar una carta por turno y la partida se siente lenta.

| Energía por turno | Distribución de coste recomendada en el mazo | Sensación |
|---|---|---|
| 3 (inicio de partida) | 40 % coste 1 · 40 % coste 2 · 20 % coste 3+ | Ágil, varias cartas por turno |
| 4-5 (mitad de partida) | 30 % coste 1 · 35 % coste 2 · 35 % coste 3+ | Más opciones por turno, sin volverse trivial |

⚠️ Esta tabla es una **convención de diseño extendida en el subgénero**, no una fórmula única
verificada en una fuente primaria — ajústala con `13 · 19` (cuando exista, simulación Monte
Carlo del mazo) o con playtesting real, como cualquier curva de `13 · 01 §4.4`.

#### 3.4.5 · Recompensas entre combates: adelgazar el mazo como decisión

Tras ganar un combate se ofrecen (típicamente) 3 cartas a elegir, o ninguna — **rechazar la
recompensa y no añadir nada al mazo es una opción válida y a veces la mejor**, porque cada carta
que entra en el mazo diluye la probabilidad de robar las que ya funcionan. Esto conecta
directamente con la meta-progresión de
[13 · 16 §2.6 — El patrón de monedas múltiples](<../13 - Diseño y producción de videojuegos/16 - Progresión - árboles de habilidades, desbloqueos y meta-progresión.md#26-el-patrón-de-monedas-múltiples-partida-frente-a-meta>):
el mazo de la partida es la moneda que se pierde al morir (o al terminar la run con éxito);
cualquier desbloqueo permanente entre partidas (nuevas cartas que pueden aparecer en próximas
runs) es la otra moneda, la que persiste — igual que el `RunState`/`MetaProgress` que `04 · 05
§4.7` ya separa para el roguelike.

```gml
/// @func generar_recompensa_cartas(_rareza_pool, _rng)
/// @desc 3 cartas al azar, ponderadas por rareza. "No elegir ninguna" se
///       resuelve en la UI (un botón "saltar"), no aquí.
function generar_recompensa_cartas(_rareza_pool, _rng)
{
    var _pesos = { comun: 70, rara: 25, epica: 5 };   // ⚠️ convención de género, ajustar con playtest
    var _resultado = [];

    repeat (3)
    {
        var _r = _rng.float() * 100;
        var _acumulado = 0;
        var _rareza_elegida = "comun";
        var _claves = struct_get_names(_pesos);
        for (var _i = 0; _i < array_length(_claves); _i++)
        {
            _acumulado += _pesos[$ _claves[_i]];
            if (_r <= _acumulado) { _rareza_elegida = _claves[_i]; break; }
        }

        var _candidatas = array_filter(_rareza_pool, function(_c) { return _c.rareza == _rareza_elegida; });
        if (array_length(_candidatas) > 0)
        {
            array_push(_resultado, _candidatas[_rng.int(array_length(_candidatas) - 1)]);
        }
    }
    return _resultado;
}
```

### 3.5 · Errores clásicos y cómo evitarlos

- **Robar del descarte sin barajarlo primero.** Si el mazo se vacía a mitad de un robo múltiple
  y el código simplemente concatena el descarte al mazo sin `_rng.shuffle()`, las últimas cartas
  jugadas se vuelven las primeras en robarse siempre — previsible y explotable.
- **Cobrar el coste de energía después de resolver el efecto, no antes.** Si `resolver_efecto()`
  se ejecuta antes de comprobar `energia >= coste`, una carta puede "colarse" con energía
  negativa. `jugar_carta()` en `§3.4.3` comprueba y cobra antes de resolver nada, a propósito.
- **Compartir el mismo struct de `CartaDef` entre todas las copias en el mazo.** Sin
  `variable_clone()` (`§3.4.2`), mejorar una copia de "Golpe" mejora TODAS las copias de
  "Golpe" del mazo, porque son la misma referencia en memoria — el mismo error de fondo que el
  `array_create` con relleno compartido de `§2.4.1`.
- **Una función de efecto distinta por cada carta, escrita a mano.** Funciona con 10 cartas; con
  100 se convierte en 100 funciones que hay que mantener sincronizadas con el catálogo. El
  intérprete genérico de `§3.4.3` es más código al principio y mucho menos código al final.
- **Ofrecer siempre 3 recompensas sin la opción de rechazarlas.** Un mazo que crece sin límite se
  vuelve peor en promedio (más cartas irrelevantes que robar); "no gracias" tiene que ser una
  opción tan válida como elegir una carta.

### 3.6 · TCG competitivo (PvP)

El deckbuilder de `§3.1`-`§3.4` asume, sin decirlo hasta ahora explícitamente, **un jugador
contra una IA**: la propia biblioteca ya lo advertía en `§3.1` al descartar la Card Game
Template de GameMaker por no traer "combate, maná ni recompensas entre partidas". Un TCG
competitivo (*Hearthstone*, *MTG Arena*, *Legends of Runeterra*) cambia esa premisa por completo:
el rival ya no es un script que decide su jugada en el mismo *frame* en el que se resuelve —
es **otro jugador real**, conectado por red, cuya mano nadie más que él puede ver. Esta
subsección **no reescribe** `Mazo()`, `CartaDef`, `CartaInstancia`, `resolver_efecto()` ni
`jugar_carta()` de `§3.4.1`-`§3.4.3`: los reutiliza tal cual y añade solo lo que cambia al pasar
de un bando con energía a dos, y de una IA sin secretos a un rival con mano oculta.

#### 3.6.1 · Qué cambia frente al deckbuilder de un jugador

| Aspecto | `§3` (un jugador contra IA) | `§3.6` (TCG competitivo, PvP) |
|---|---|---|
| **Mano rival** | La IA no tiene mano que ocultar: decide su jugada con un script que el propio motor ejecuta, información perfecta para el juego | Información imperfecta: solo se conoce la **cantidad** de cartas del rival, nunca su contenido, hasta que se juegan |
| **Energía** | Un solo bando la tiene (el jugador; `§3.4.4`) | **Los dos bandos** tienen su propia energía, cada turno |
| **Turnos** | El jugador juega hasta pasar; la IA enemiga resuelve aparte | Turnos alternos entre **dos jugadores reales**, arbitrados por el servidor |
| **Quién resuelve `jugar_carta()`** | El propio cliente: no hay a quién engañar | Solo el **servidor** (`§3.6.5`); ningún cliente la ejecuta en local |
| **RNG del combate** | `RNG()` de `§3.4.2`, con semilla propia | La misma `RNG()`, pero corriendo **una sola vez, en el servidor** — nunca una tirada distinta por cliente (`§3.6.7`) |

#### 3.6.2 · Mano rival: un número, nunca un array de cartas

La mano oculta es el rasgo que define al género frente a cualquier IA de tablero con
información perfecta. [04 · 31 §10 bis — Búsqueda adversarial: minimax y poda
alfa-beta](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md#10-bis--búsqueda-adversarial-minimax-y-poda-alfa-beta)
es justo la técnica contraria: minimax **exige** que ambos bandos vean el estado completo del
otro para explorar su árbol de jugadas, y ese mismo documento ya señala por qué un TCG con mano
oculta queda fuera de su alcance — haría falta *Perfect Information Monte Carlo*,
*Counterfactual Regret Minimization*, o, más simple, reglas/*utility* sobre lo que sí es
visible (el tablero de `§3.6.3`). Aquí no hace falta ninguna de las dos: la regla es más básica
y de red, no de IA — ningún cliente, ni el motor del servidor hacia el cliente equivocado,
puede filtrar el contenido de la mano rival.

Que la mano sea información oculta mientras el resto del estado es público no es una convención
inventada para este documento: las reglas oficiales de *Magic: The Gathering* tratan la mano
explícitamente como *hidden zone* — regla 101.4a, citada en `§ Fuentes`. La consecuencia para
GameMaker es literal: el servidor **nunca serializa** el array de `CartaInstancia` de la mano
rival hacia el cliente contrario, solo su longitud.

```gml
/// @func BandaCombatePvp(_net_id, _mazo, _energia_maxima)
/// @desc Un bando del combate. Reutiliza el Mazo() de §3.4.1 sin cambios y le
///       añade lo que en un jugador contra IA no hacía falta: DE QUIÉN es
///       (net_id, nunca el id de instancia — §2.4 de 04 · 14) y su propia
///       energía, porque ahora hay dos bandos con energía, no uno.
function BandaCombatePvp(_net_id, _mazo, _energia_maxima) constructor
{
    net_id          = _net_id;
    mazo            = _mazo;               // Mazo() de §3.4.1, sin reescribir
    energia         = 0;
    energia_maxima  = _energia_maxima;
    cartas_en_juego = [];                  // CartaInstancia ya jugadas: público para ambos
}
```

```gml
// obj_combate — Create (extensión PvP sobre §3.2; NO sustituye su Create de un jugador)
banda = [
    new BandaCombatePvp(net_id_jugador_a, new Mazo(baraja_jugador_a), 3),
    new BandaCombatePvp(net_id_jugador_b, new Mazo(baraja_jugador_b), 3)
];
rng             = new RNG(global.semilla_combate);   // §3.4.2: una sola RNG, compartida
turno_de_net_id = banda[0].net_id;                    // el servidor decide quién empieza
```

#### 3.6.3 · Tablero y maná: lo que sí es público

Una vez una carta se juega, deja de ser secreto: en cualquier TCG de mesa o digital, las
criaturas o hechizos ya resueltos sobre el tablero, la vida de cada bando y la energía
disponible de ambos son información visible para los dos jugadores — lo único oculto es la
mano. El paquete que el servidor manda a cada cliente tras cualquier cambio de estado refleja
exactamente esa frontera:

```gml
/// @func tablero_serializar_para_cliente(_banda_propia, _banda_rival)
/// @desc "Propia" y "rival" son relativas a quién va a recibir el paquete: el
///       servidor llama a esto una vez por cliente, intercambiando qué banda
///       es cuál. La mano propia va completa (es SUYA); la del rival, solo
///       su longitud. El tablero y la energía de ambos bandos van completos.
function tablero_serializar_para_cliente(_banda_propia, _banda_rival)
{
    return {
        energia_propia         : _banda_propia.energia,
        energia_maxima_propia  : _banda_propia.energia_maxima,
        energia_rival          : _banda_rival.energia,                    // público: es del tablero
        mano_propia            : _banda_propia.mazo.mano,                  // completa: es SUYA
        mano_rival_cantidad    : array_length(_banda_rival.mazo.mano),     // solo el número
        tablero_propio         : _banda_propia.cartas_en_juego,
        tablero_rival          : _banda_rival.cartas_en_juego,             // jugada = pública
        turno_de_net_id        : obj_combate.turno_de_net_id
    };
}
```

El envío real de este struct como paquete de red —convertirlo a buffer y mandarlo por el
socket— es exactamente el formato de
[04 · 14 §4.2 — Buffers: el formato de los paquetes](./14%20-%20Multijugador.md) y la recepción
del snapshot de
[04 · 14 §5.5 — Recibir el snapshot e interpolar](./14%20-%20Multijugador.md); no se repite
aquí. La única diferencia real frente a un shooter en red es **qué campos se omiten** para el
bando equivocado, no el mecanismo de transporte.

#### 3.6.4 · Turnos alternos entre dos jugadores reales

`§3.3` resuelve el turno con un único booleano implícito ("es el turno del jugador o no"). En
PvP hacen falta **dos** "en turno", uno por bando, y solo el servidor decide cuál vale — nunca
un campo que mande el propio cliente:

```gml
/// @func es_mi_turno()
/// @desc Se ejecuta en el CLIENTE, solo para decidir si mostrar los controles
///       activos (arrastrar cartas, botón de pasar turno). NO autoriza nada:
///       la autoridad real está en el servidor (§3.6.5). El id propio del
///       cliente NO es una global nueva: es `objNetManager.mi_id`, el mismo
///       que ya asigna `NetMsg.server_welcome` en 04 · 14 §5.4 — no lo
///       dupliques en un global.net_id_local que nadie llegaría a escribir.
function es_mi_turno()
{
    return (obj_combate.turno_de_net_id == objNetManager.mi_id);
}

/// @func avanzar_turno_pvp()
/// @desc Solo la ejecuta el SERVIDOR, al final de cada turno. Alterna qué
///       bando manda y le da su fase de inicio de turno — el mismo paso 2
///       de §3.3, ahora una vez por bando en vez de una vez por partida.
function avanzar_turno_pvp()
{
    var _indice_siguiente = (obj_combate.turno_de_net_id == obj_combate.banda[0].net_id) ? 1 : 0;
    var _banda            = obj_combate.banda[_indice_siguiente];

    _banda.energia = _banda.energia_maxima;              // §3.3 paso 2, un bando a la vez
    _banda.mazo.robar(1, obj_combate.rng);                // §3.4.1, sin cambios; 1 carta por turno

    obj_combate.turno_de_net_id = _banda.net_id;
}
```

#### 3.6.5 · Autoridad del servidor: reutilizar `jugar_carta()` sin reescribirla

[04 · 14 §2.2 — Nunca confíes en el cliente](./14%20-%20Multijugador.md) se aplica aquí carta a
carta: el cliente manda la **intención** ("quiero jugar la carta N contra ese objetivo"), y solo
el servidor la resuelve. El problema práctico es que `jugar_carta()` (`§3.4.3`) fue escrita
pensando en un único bando: lee `obj_combate.mazo`, `obj_combate.energia` y `obj_combate.jugador`
directamente, sin recibir de qué bando se trata como parámetro. Reescribirla para aceptar dos
bandos violaría la regla de no tocar `§3.4.3` — la alternativa, sin cambiar una sola línea de
`jugar_carta()`, es apuntar esos tres campos al bando que tiene el turno **antes** de llamarla:

```gml
/// @func resolver_jugada_pvp_en_servidor(_net_id_autor, _indice_mano, _objetivo)
/// @desc Solo se ejecuta en el SERVIDOR. Comprueba que quien pide la jugada
///       es quien de verdad tiene el turno (comparado contra el net_id de
///       quien mandó el paquete, no contra un campo que el cliente afirme
///       ser él) y solo entonces apunta obj_combate a su bando y llama a
///       jugar_carta() (§3.4.3) sin tocarla.
function resolver_jugada_pvp_en_servidor(_net_id_autor, _indice_mano, _objetivo)
{
    if (_net_id_autor != obj_combate.turno_de_net_id) return false;   // no es su turno: se ignora

    var _banda = (obj_combate.banda[0].net_id == _net_id_autor) ? obj_combate.banda[0] : obj_combate.banda[1];
    obj_combate.mazo    = _banda.mazo;      // struct: es una referencia — jugar_carta() muta el original
    obj_combate.jugador = _banda.jugador;   // ídem: sin copia, sin necesidad de devolverlo
    obj_combate.energia = _banda.energia;   // número: se copia por VALOR, no por referencia

    var _jugada_valida = jugar_carta(_indice_mano, _objetivo);   // §3.4.3, sin cambios

    _banda.energia = obj_combate.energia;   // el número no se actualiza solo: hay que devolverlo a mano
    return _jugada_valida;
}
```

La distinción entre `mazo`/`jugador` (structs, referencias — se mutan solos) y `energia` (un
número, copiado por valor — hay que reescribirlo a mano tras la jugada) es la misma que
`§3.4.2` ya advierte con `variable_clone`: en GML, olvidar si algo es referencia o valor es la
fuente más repetida de bugs de este bloque entero.

#### 3.6.6 · Síncrono o asíncrono

Todo lo anterior asume un modelo **síncrono**: los dos jugadores conectados a la vez sobre el
mismo socket persistente de `04 · 14` (su `objNetManager` y su evento asíncrono de red, `§5.4`
de ese documento). Es el modelo correcto para una partida en vivo, y el que recomienda la tabla
de [04 · 14 §2.1](./14%20-%20Multijugador.md) para cualquier juego competitivo: autoridad del
servidor, nunca P2P.

Muchos TCG competitivos ofrecen además un modo **asíncrono** ("juega tu turno cuando puedas",
partidas que duran horas o días) sobre peticiones HTTP en vez de un socket persistente: un
jugador manda su jugada, el servidor la valida y la guarda, el otro la recibe la próxima vez
que abre la app. [04 · 17 §5 — Comunicarte con tu propio servidor](./17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)
ya cubre la pieza de transporte (`http_post_string`, la respuesta en el evento *Async - HTTP*),
pero ⚠️ **esta biblioteca no tiene todavía un documento dedicado al diseño de una cola de
turnos pendientes** (qué se guarda entre peticiones, cómo se notifica al otro jugador, qué pasa
si nunca vuelve a abrir la partida). Si tu TCG lo necesita, esa es la pieza que falta — no la
inventes a partir de este documento: es contenido para un documento futuro sobre turnos
asíncronos, no algo que `§3.6` resuelva por extensión.

#### 3.6.7 · Errores clásicos del PvP que `§3.5` no cubre

- **Mandar el array completo de `CartaInstancia` de la mano rival "por si acaso".** Aunque el
  cliente no lo pinte en pantalla, cualquiera puede leerlo con un inspector de paquetes o un
  editor de memoria — la regla de `§3.6.2` no es solo de diseño, es de seguridad: lo que el
  servidor no manda, no se puede robar.
- **Dejar que cada cliente tire su propio dado para un efecto aleatorio de carta** ("inflige
  entre 2 y 6 de daño"). Si cada cliente resuelve el azar por su cuenta, los dos bandos ven un
  resultado distinto y el estado diverge. El único que tira es el servidor, con la `RNG()` única
  de `§3.6.1`, y difunde el resultado ya resuelto — el mismo problema de determinismo que
  [04 · 14 §2.1](./14%20-%20Multijugador.md) resuelve para el lockstep, aplicado carta a carta.
- **Comprobar el turno con un campo que manda el propio cliente** ("soy_yo: true"). El servidor
  compara siempre contra el `net_id` de quien envió el paquete (`§3.6.5`), nunca contra un dato
  que el mensaje afirme sobre sí mismo.
- **Confundir "deshabilitar el botón en la UI" con "validar el turno".** Un cliente modificado
  puede mandar el paquete igual aunque el botón esté gris — `resolver_jugada_pvp_en_servidor()`
  es la única barrera real.

---

## 4 · Checklist transversal

- [ ] **[Los tres]** El bucle de decisión (elegir build) y el bucle de resolución (ejecutar la
      build) están separados en el código, no entrelazados — `§0.2`.
- [ ] **[Los tres]** Toda moneda de partida (XP, oro, energía) tiene un sumidero explícito y se
      puede detectar su inflación con el método de `13 · 01 §4.3` — `§0.4`.
- [ ] **[Los tres]** El escalado de dificultad usa una curva con razón fija (geométrica), no una
      suma lineal — `§0.5`, `13 · 01 §4.4`.
- [ ] **[Bullet heaven]** Ningún enemigo, proyectil propio ni recogible de XP se crea o destruye
      fuera de un `Pool` una vez la partida ha empezado — `§1.4.5`.
- [ ] **[Bullet heaven]** Las armas disparan solas por temporizador; no hay ningún `if
      (keyboard_check(...))` en el camino de disparo — `§1.4.1`.
- [ ] **[Autobattler]** El tablero se congela (snapshot) antes de simular el combate; el
      jugador no puede mover unidades a mitad de la simulación — `§2.3`.
- [ ] **[Autobattler]** El combate se simula con una `RNG` de semilla propia, nunca con
      `random()` global — `§2.4.5`.
- [ ] **[Autobattler]** El interés tiene un techo explícito — `§2.4.3`.
- [ ] **[Deckbuilder]** Cada `CartaInstancia` en el mazo es una copia única
      (`variable_clone`), nunca una referencia compartida al `CartaDef` del catálogo — `§3.4.2`.
- [ ] **[Deckbuilder]** El coste de energía se cobra ANTES de resolver el efecto de la carta —
      `§3.4.3`.
- [ ] **[Deckbuilder]** "No elegir ninguna recompensa" es una opción real en la UI, no solo en
      la teoría — `§3.4.5`.
- [ ] **[Deckbuilder PvP]** La mano rival nunca se serializa hacia el cliente contrario: el
      servidor solo manda `array_length(...)`, nunca el array de `CartaInstancia` — `§3.6.2`.
- [ ] **[Deckbuilder PvP]** `jugar_carta()` solo se ejecuta en el servidor, y solo tras comprobar
      que el `net_id` que pide la jugada coincide con `turno_de_net_id` — `§3.6.5`.

---

## Ver también

- [04 · 03 — Shoot 'em up (shmup)](./03%20-%20Shoot%20em%20up%20%28shmup%29.md) — *object
  pooling* de proyectiles (§4.5-4.7) y `WaveDef`/`objWaveDirector` (§5.2-5.3), el modelo de
  oleadas dirigidas por datos que `§1.4.2` adapta a una curva continua.
- [`06 - Assets y Scripts/scr_pool.gml`](<../06 - Assets y Scripts/scr_pool.gml>) — el
  constructor `Pool` completo que `§1.4.5` y `§1.5.3` usan tal cual, sin reescribirlo.
- [13 · 08 §4 — Particionado espacial](<../13 - Diseño y producción de videojuegos/08 - Físicas a mano y fluidos.md#4--particionado-espacial-colisiones-cuando-hay-cientos-de-cosas>) —
  el *spatial hash* (`rejilla_nueva`/`rejilla_insertar`/`rejilla_vecinos`) para el caso extremo
  de miles de entidades como *structs*, que `§1.4.5` cita sin repetir.
- [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  `dano_resolver()` y `DanoTipo`, el pipeline al que se enganchan el daño de área de `§1.4.6`,
  el combate simulado de `§2.4.5` y los efectos de carta de `§3.4.3`.
- [04 · 36 — Habilidades, enfriamientos y recursos de combate](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md) —
  el patrón de struct-dirigido-por-datos (§1.2, §3.1) que `§1.5.0`, `§2.2` y `§3.4.3` reutilizan
  para armas, unidades y cartas respectivamente.
- [13 · 16 — Progresión: árboles de habilidades, desbloqueos y meta-progresión](<../13 - Diseño y producción de videojuegos/16 - Progresión - árboles de habilidades, desbloqueos y meta-progresión.md>) —
  poder frente a opciones (§2.5) y el patrón de monedas múltiples (§2.6), la meta-progresión
  entre partidas que los tres géneros de este documento dejan fuera de la run.
- [13 · 01 §4 — Economía y balance](<../13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md#4--economía-y-balance>) —
  el vocabulario de *pool*/fuente/sumidero, la regla del sumidero obligatorio y la curva de
  coste geométrica que `§0.4`, `§1.4.2` y `§2.4.3` aplican sin repetir.
- [04 · 05 §4.1 y §5.0 — Roguelike y generación procedural](./05%20-%20Roguelike%20y%20generación%20procedural.md) —
  el constructor `RNG()` con semilla que `§2.4.5` y `§3.4.2` reutilizan, y el patrón de moneda
  dual `RunState`/`MetaProgress` (§4.7) que `§3.4.5` cita para la meta-progresión de cartas.
- [13 · 13 §5.5 — Bolsa aleatoria (*shuffle bag*)](<../13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md#55--bolsa-aleatoria-shuffle-bag>) —
  la herramienta correcta si el generador de recompensas de `§3.4.5` repite la misma carta
  demasiado seguido.
- [13 · 13 §8 — Curvas de crecimiento para diseño](<../13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md#8--curvas-de-crecimiento-para-diseño>) —
  las cinco formas de curva que `§0.5` aplica a XP, vida enemiga, energía y oro sin repetir la
  teoría.
- [07 · 06 — Plantillas y starters](<../07 - Ecosistema/06 - Plantillas y starters.md>) —
  la **Survivor Game Template** oficial (§1.1 de esa tabla) que `§1.4.2` analiza con código
  real descargado, y la **Card Game Template** (tipo solitario) que `§3.1` descarta como punto
  de partida para un *deckbuilder* de combate.
- [04 · 13 — Estrategia y gestión](./13%20-%20Estrategia%20y%20gestión.md) —
  selección múltiple, grid y UI Layers/Flex Panels (§4.1-4.2, §4.7) que `§2.2` reutiliza para el
  tablero y la tienda del autobattler; la fila de tabla que este documento amplía.
- [04 · 09 — Survival y crafting](./09%20-%20Survival%20y%20crafting.md) —
  el género con el que `§1.1` distingue *bullet heaven* por compartir la palabra
  «supervivencia»: necesidades sin amenaza activa, frente a horda sin tregua.
- [04 · 02 — Top-Down / Twin-Stick](<./02 - Top-Down _ Twin-Stick.md>) —
  el disparo apuntado manualmente que `§1.1` usa como contraste con las armas automáticas de
  *bullet heaven*.
- [04 · 14 — Multijugador](./14%20-%20Multijugador.md) §2 y §2.2 — el modelo de autoridad del
  servidor y la regla «nunca confíes en el cliente» que `§3.6.5` aplica carta a carta; también
  §2.4 (la regla del `net_id`) que `§3.6.4` reutiliza para saber de quién es el turno, y §4.2 y
  §5.5 (formato de paquetes y recepción del snapshot) a los que `§3.6.3` engancha su struct de
  estado visible sin repetir el transporte.
- [04 · 17 §5 — Comunicarte con tu propio servidor](./17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) —
  las peticiones HTTP asíncronas (`http_post_string`) que `§3.6.6` cita como la pieza de
  transporte de un TCG asíncrono, honesto sobre lo que esta biblioteca no cubre todavía (la cola
  de turnos pendientes).
- [04 · 31 §10 bis — Búsqueda adversarial: minimax y poda alfa-beta](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md#10-bis--búsqueda-adversarial-minimax-y-poda-alfa-beta) —
  la técnica de información perfecta que `§3.6.2` usa como contraste directo con la mano oculta
  de un TCG; ese mismo documento ya cita este bloque para explicar por qué el deckbuilder de
  `§3` no es candidato a minimax.

---

## Fuentes

- **poncle**, ficha oficial de *Vampire Survivors* en itch.io —
  <https://poncle.itch.io/vampire-survivors> (consultado 2026-09-06; descripción del juego,
  duración de sesión «about a half-hour», ejemplos de evolución de armas «Bloody Tear»/«Heaven
  Sword», y la frase «gather gold... for the next survivor» sobre meta-progresión).
- **Steam**, ficha de *Vampire Survivors* —
  <https://store.steampowered.com/app/1794680/Vampire_Survivors/> (consultado 2026-09-06;
  descripción «a time survival game with minimalistic gameplay and roguelite elements» y
  recomendaciones de estrategia sobre concentrar mejoras en pocas armas).
- **Steam**, ficha de *Slay the Spire* —
  <https://store.steampowered.com/app/646570/Slay_the_Spire/> (consultado 2026-09-06; cita
  textual «the best single player deckbuilder we could» y la característica «Dynamic Deck
  Building»).
- **Steam**, ficha de *Super Auto Pets* —
  <https://store.steampowered.com/app/1714040/Super_Auto_Pets/> (consultado 2026-09-06; «Build
  a team of cute pets with unique abilities. Battle against other players» y el formato de
  vidas «10 wins before losing all your hearts»).
- **API oficial de GameMaker**, catálogo de plantillas —
  <https://api.gamemaker.io/api/gamemaker/project-templates> (consultado 2026-09-06; ficha de
  la **Survivor Game Template**, `package_id: com.gamemaker.farmsurvivorcode`, versión 1.0.3, y
  de la **Card Game Template**, `package_id: com.gamemaker.cardgame`, versión 1.1.3 — la misma
  fuente que ya usa `07 · 06`).
- **Paquete real descargado** de la Survivor Game Template (`com.gamemaker.farmsurvivorcode`
  v1.0.3, vía `api.yoyogames.com`, descargado y leído completo el 2026-09-06): código fuente de
  `next_wave()`, `spawn_enemy()`, `get_upgrades()`, `weapon_shooting_upgrades()` y los objetos
  `obj_game`/`obj_enemy`/`obj_upgrade`/`obj_button_reroll`, citados literalmente en `§1.4.2`,
  `§1.4.3` y `§1.4.4`. Es la fuente primaria de los números concretos de esa sección (razón
  1,2 en la meta de XP, −3 fotogramas de *spawn* por oleada, ×1,25 de vida enemiga, 10 oleadas
  totales, *reroll* gratuito).
- Manual oficial — `array_create` (aviso explícito sobre relleno por referencia compartida, la
  base del error clásico de `§2.4.1` y `§3.5`) —
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/array_create.htm>
- `13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance
  y dificultad.md` — vocabulario de economía y curva de coste geométrica, citados sin repetir en
  `§0.4`, `§0.5`, `§1.4.2` y `§2.4.3`.
- `04 - Recetas por género/05 - Roguelike y generación procedural.md` — constructor `RNG()` con
  semilla (§5.0) y el patrón `RunState`/`MetaProgress` (§4.7), reutilizados en `§2.4.5` y
  `§3.4.2`.
- ⚠️ **Teamfight Tactics** (Riot Games): se intentó verificar la fórmula exacta de interés y las
  probabilidades de tienda por nivel contra fuentes oficiales
  (<https://teamfighttactics.leagueoflegends.com/en-us/>,
  <https://support-leagueoflegends.riotgames.com/>); ninguna de las dos páginas alcanzables sin
  autenticación publica los números de forma estable citable, y las páginas de terceros
  habituales para esto (fandom, mobalytics) devolvieron 402/403 al intentarlo con `curl` y con
  `WebFetch`. Los valores de `§2.4.3` (tramo de 10 de oro, techo de 5 de interés) se presentan
  explícitamente como convención de género, no como cifra verificada de un juego concreto.
- ⚠️ **Dota Auto Chess** y **Dota Underlords**: citados solo por su papel histórico en el
  género (`§2.1`), sin verificación de mecánica concreta — Underlords está retirado de Steam y
  su ficha ya no sirve como fuente primaria viva.
- **Wizards of the Coast**, *Magic: The Gathering Comprehensive Rules* (edición del
  19-08-2026) — <https://media.wizards.com/2026/downloads/MagicCompRules%2020260819.txt>
  (consultado 2026-09-07; regla **101.4a**: *"If an effect has each player choose a card in a
  hidden zone, such as their hand or library, those cards may remain face down as they're
  chosen"* — confirma la mano como *hidden zone* frente al resto del estado del juego, la base
  de `§3.6.2`).
- ⚠️ **Hearthstone** (Blizzard) y **Legends of Runeterra** (Riot Games): citados en `§3.6` solo
  como ejemplos del género para orientar al lector, sin cifra ni cita textual propia —
  `hearthstone.blizzard.com` y `playruneterra.com` no resolvieron por DNS al intentarlo con
  `curl` ni con `WebFetch` el 2026-09-07, y la ficha de Steam de *Legends of Runeterra*
  (`app/1364780`) devolvió la página de otro juego. Ningún dato concreto de estos dos títulos se
  usa en `§3.6`: el patrón de mano oculta / tablero visible se sostiene con la regla 101.4a de
  Magic (arriba) y con las piezas ya verificadas de la biblioteca (`Mazo()`, `CartaDef` de
  `§3.4.1`-`§3.4.3`).
- `_indice/auditorias/diseno-gdd.md` — propuesta 7, el encargo de este documento.
