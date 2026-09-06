# 35 · Combate por turnos y táctico en rejilla

> **Dificultad:** media-alta · **Antes de esto:** el bucle mínimo de combate por turnos de
> [04 · 04 §5.6](./04%20-%20RPG%20_%20Action%20RPG.md) (`BattleState`, `Stats`) funcionando.
> Para la mitad táctica conviene además conocer
> [06 · `scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml)
> y las conversiones de rejilla de
> [13 · 13 §7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md).
>
> Este documento **sustituye a `04 · 04 §5.6`** como referencia de combate por turnos: donde
> aquel era el mínimo viable (siempre ataca a `enemigos[0]`, sin objetivo, sin habilidades),
> aquí está el sistema completo — orden de turnos por **iniciativa** y por **ATB**, con la cola
> visible; **selección de objetivo** con cursor y validación de alcance; **habilidades y
> hechizos con coste**, leídos de datos y enganchados al motor de estados y al pipeline de daño
> de [04 · 32](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md); y el **menú de
> batalla completo** (comando → submenú → objetivo → confirmación → retroceso). Y la mitad
> **táctica**: rango de movimiento por coste con Dijkstra sobre una rejilla, resaltado de
> casillas, alcance de ataque y línea de tiro, bonus de terreno y altura, e IA de posicionamiento
> por utilidad.
>
> **Qué NO cubre este documento** (y dónde está): el motor de tipos de daño, armadura, escudos
> y efectos de estado en sí —veneno, aturdimiento, quemadura— vive en
> [04 · 32](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md); aquí se **usa**
> `dano_resolver()` y `MotorEfectos`, no se reescriben. El gestor de habilidades con enfriamiento
> en **tiempo real**, cargas, tiempo de casteo interrumpible y el árbol de progresión vive en
> [04 · 36 — Habilidades, enfriamientos y progresión de
> combate](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md); en
> combate por turnos casi nada de eso hace falta (el «enfriamiento» es simplemente que la unidad
> ya actuó esta ronda), así que aquí sólo se reutiliza la idea de **habilidad como dato**, no su
> código — comparte el mismo `habilidades.json` si te conviene. Los arquetipos de enemigo, la
> tabla de amenaza y el director de intensidad de un encuentro son de
> [04 · 33](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md).
> El árbol de comportamiento, el utility AI genérico y la percepción son de
> [04 · 31](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md);
> aquí sólo se **aplican** sus curvas a un problema nuevo (elegir una celda). El *deckbuilding*
> (mazo, mano, energía por turno) sigue siendo un hueco de la biblioteca y no se cubre aquí.

---

## 1. Los principios

### 1.1 El turno es una máquina de estados; el menú, una pila

`04 · 04 §5.6` ya lo dice: un combate por turnos es una máquina de estados —
`intro → turno_jugador → turno_enemigo → resolviendo → victoria/derrota`— y esa máquina se
reutiliza tal cual para diálogos y menús. Lo que ese mínimo viable no muestra es que **dentro**
de `turno_jugador` hay una SEGUNDA máquina, más fina: el menú de batalla no es un estado, es una
**pila**. «Atacar» abre un submenú de objetivos; «Habilidad» abre un submenú de habilidades que
a su vez abre uno de objetivos; cancelar en cualquier punto vuelve exactamente un nivel atrás,
no a la pantalla de inicio. Modelarlo como una pila de contextos (`array_push`/`array_pop`) en
vez de como un enum plano con banderas (`en_submenu_habilidad`, `en_submenu_objetivo`...) es lo
que hace que «retroceder» sea **una sola función**, sin importar en qué profundidad estés — la
misma idea que un navegador con «atrás», no una serie de `if` por pantalla.

### 1.2 Iniciativa frente a ATB: dos relojes distintos

Hay dos convenciones consolidadas para decidir quién actúa a continuación, y no son la misma
mecánica con arte distinto:

| | Iniciativa (por ronda) | ATB (*Active Time Battle*) |
|---|---|---|
| Qué mide | Un orden, no un tiempo: se calcula una vez y se recorre | Un progreso continuo: cada unidad llena una barra a su propio ritmo |
| Quién actúa rápido | El más rápido actúa **antes** en la ronda | El más rápido actúa **más veces** por minuto |
| Interfaz mínima | Una lista ordenada (retrato + nombre) | Una barra por unidad, o una cola con las próximas N |
| Origen | RPG de mesa (D&D: `1d20 + modificador de Destreza`) y JRPG por rondas (*Dragon Quest*) | *Final Fantasy IV* (1991), inventado por Hiroyuki Ito |
| Con quién combina bien | Táctica en rejilla: «toda mi facción mueve, luego la enemiga» es más fácil de leer sobre un mapa | Acción con pausa: da tensión sin exigir reflejos |

El ATB nació de una idea muy concreta: Ito observó la Fórmula 1 y pensó que un coche más rápido
completa más vueltas en el mismo tiempo — de ahí que un personaje veloz actúe más veces, no sólo
antes. Tiene dos modos de reloj, y la diferencia importa para la sensación del juego:

- **Activo**: las barras siguen llenándose mientras navegas el menú. Te pueden golpear
  eligiendo qué hacer. Tensión constante.
- **Espera** (*Wait*): las barras se congelan en cuanto se abre un menú. Es el modo que
  recomienda la tabla de accesibilidad de `04 · 04 §4.4` («empieza por turnos: sin presión de
  tiempo»), y el que implementa el código base de este documento por defecto — un interruptor
  lo cambia a Activo sin tocar el resto de la lógica.

**Cuál elegir**: la iniciativa es más simple de implementar y de leer sobre una rejilla táctica
grande (por eso *Fire Emblem* y *Final Fantasy Tactics* la usan: «bando jugador, luego bando
enemigo»); el ATB da más textura a un JRPG con pocos combatientes y pantalla de combate propia.
Nada impide mezclarlos —rejilla táctica con ATB por unidad—, pero es más trabajo por poco
beneficio si no tienes una razón de diseño concreta.

### 1.3 La cola de turnos como interfaz

Mostrar **quién actúa después** cambia el juego de «reactivo» a «planificable»: si el jugador ve
que el sanador enemigo actúa en dos turnos, curar antes de rematarlo pasa de ser una corazonada
a una decisión informada. *Into the Breach* lleva esto al extremo con **información perfecta**:
enseña la casilla y la dirección exactas del próximo ataque de cada enemigo *antes* de que el
jugador mueva, convirtiendo el combate en un rompecabezas de posicionamiento en vez de una
prueba de reflejos. La cola de turnos de este documento es la versión ligera de esa misma idea:
no hace falta enseñar el ataque exacto, basta con enseñar **el orden**.

### 1.4 Selección de objetivo: alcance como validación, no como sugerencia

`enemigos[0]` (el mínimo de `04 · 04`) funciona con un enemigo. Con más de uno, el jugador
necesita **elegir**, y el motor necesita **validar** — dos problemas distintos:

1. **Candidatos**: qué unidades son objetivo legal para esta acción (un hechizo de curación no
   ofrece enemigos como objetivo; un ataque cuerpo a cuerpo, en modo táctico, no ofrece un
   objetivo fuera de alcance).
2. **Cursor**: cómo se recorre esa lista de candidatos. En una lista corta, **envolver** es
   correcto (`13 · 05 §2.2`: «Lista vertical corta ≤ 8 → sí envuelve»); en la rejilla táctica, el
   cursor se mueve por el mapa, no por una lista, y sólo se puede **confirmar** sobre una celda
   resaltada — exactamente el patrón «insistir en un botón inactivo merece una respuesta» de
   `13 · 05 §3.5 a)`.

### 1.5 El menú de batalla como pila de contextos

Cuatro niveles, uno empujado sobre el anterior: **comando** (Atacar / Habilidad / Objeto /
Defender / Huir) → **submenú** (qué habilidad, qué objeto) → **objetivo** (a quién) →
**confirmación** (¿seguro?). El foco, el orden y la envolvente de cada nivel son los mismos
conceptos de `13 · 05 §2.2` (las cinco leyes del foco, la tabla de envolvente); lo único nuevo
aquí es apilarlos.

### 1.6 La rejilla táctica: coste de movimiento, no casillas

La confusión más común al pasar de un JRPG por turnos a uno táctico: «puede moverse 4
casillas» **no** es lo mismo que «puede moverse 4 de coste». Cruzar un pantano cuesta más que
cruzar hierba; un muro no cuesta más, es intransitable. `06 · scr_grid_pathfinding.gml` ya trae
`GridPonderado`, una rejilla con coste por celda y A* en GML puro — este documento la reutiliza
tal cual para el terreno, y añade la pieza que le falta: calcular **todas** las celdas
alcanzables con un presupuesto dado, no sólo la ruta a un destino conocido. Eso es Dijkstra
desde el origen sin destino fijo, deteniéndose cuando el coste acumulado supera el presupuesto
— BFS puro bastaría si todas las celdas costaran 1, pero en cuanto el barro cuesta más que la
hierba, BFS da resultados incorrectos y hace falta la cola de prioridad.

### 1.7 Terreno y altura como multiplicadores de decisión

*Fire Emblem* trata el terreno como una variable de combate, no de decorado: un bosque cuesta
más moverse por él pero da bonus de evasión/defensa a quien se queda dentro; una fortaleza cura
y protege. La regla de diseño es siempre la misma forma: **el terreno que más cuesta cruzar es
el que más conviene defender**, porque el enemigo paga el coste de movimiento para desalojarte.
La altura añade un segundo eje: disparar cuesta abajo suele premiarse, disparar cuesta arriba
penalizarse — es una convención de género, no una física real, y como tal se implementa como una
tabla de datos ajustable, nunca como una fórmula sagrada.

### 1.8 Línea de tiro y zona de amenaza

Dos preguntas distintas que se confunden fácil:

- **¿A qué distancia llega mi arma?** — el alcance, un número.
- **¿Hay algo en medio que lo bloquee?** — la línea de tiro, una comprobación célula a célula
  entre origen y destino, igual en espíritu al *raycasting* de campo de visión de
  `04 · 05 §5.6`, pero para un único segmento conocido en vez de para 360° alrededor de un punto.

Y una tercera, la que de verdad cambia cómo se juega: **¿qué casillas podría atacar el enemigo
si moviera primero?** — su «zona de amenaza», la unión del alcance de ataque alrededor de cada
casilla a la que puede moverse. Enseñarla es lo que permite planificar sin morir por sorpresa;
es la mecánica que hace jugable *Into the Breach* pese a su información total: sabes exactamente
dónde es seguro pisar.

### 1.9 Posicionamiento: la utilidad decide dónde, no sólo qué

`04 · 31 §8` ya resuelve «¿ataco, curo o me cubro?» puntuando opciones con curvas 0-1. Elegir
**dónde moverse** dentro de una rejilla es el mismo problema con más candidatos: en vez de tres
acciones fijas, hay una celda por cada casilla alcanzable. La solución es la misma
`elegir_por_utilidad()` — sólo cambian las **consideraciones**: exposición a la zona de amenaza
enemiga, cercanía al alcance de ataque ideal (ni pegado ni fuera de rango) y cobertura de
terreno. No hace falta un sistema nuevo, hace falta aplicar el que ya existe a más opciones.

---

## 2. Arquitectura recomendada

### 2.1 Dónde vive cada cosa

```
objBattleManager               (persistente durante el combate; existía en 04 · 04 §5.6)
├─ modo_orden      : ModoOrdenTurnos.INICIATIVA | .ATB      (§4.1 / §4.2)
├─ unidades        : Array<UnidadTactica>                    (aliados + enemigos, §5.1)
├─ cola            : Array<UnidadTactica>                    (orden calculado o predicho, §5.4)
├─ turno_actual    : UnidadTactica
├─ menu_pila       : Array<Struct>                           (§5.7 — sólo durante turno_jugador)
├─ mapa            : Struct { grid, terreno, altura, ... }   (sólo en modo táctico, §5.9)
└─ state           : BattleState.*                           (§3)

UnidadTactica                  (una por combatiente; struct colgado de una instancia o suelto)
├─ stats     : Stats                    (04 · 04 §5.0 — SIN TOCAR)
├─ combate   : EstadoCombate            (04 · 30 §6 — SIN TOCAR)
│  ├─ armadura, escudo, resistencias    (04 · 32 §5.2/§5.3/§5.1 — opcionales)
│  └─ efectos : MotorEfectos            (04 · 32 §5.4 — SIN TOCAR)
├─ equipo, nombre, habilidades[]
├─ iniciativa | atb                     (según modo_orden)
└─ celda_col, celda_fila, puntos_movimiento, alcance_ataque   (sólo modo táctico)
```

Nada de esto sustituye `Stats`, `EstadoCombate` ni `MotorEfectos`: **cuelga de ellos**, con el
mismo patrón aditivo de `04 · 32 §2.1`. Un combate por turnos sin rejilla simplemente no rellena
`celda_col`/`celda_fila`; todo el código de movimiento y línea de tiro comprueba su existencia
antes de usarlos, así que el mismo `UnidadTactica` sirve para un JRPG clásico y para un SRPG.

### 2.2 Dos niveles de máquina: turno y menú

```
BattleState (quién actúa)                    menu_pila (cómo elige, SÓLO durante turno_jugador)
┌─────────────┐                              ┌──────────────────────────────────┐
│ intro       │                              │ [ comando ]                       │
├─────────────┤   entra en turno_jugador     │ [ comando, habilidades ]          │
│turno_jugador│ ──────────────────────────►  │ [ comando, habilidades, objetivo ]│
├─────────────┤                              │ [ comando, ..., confirmacion ]    │
│turno_enemigo│   confirmar ejecuta la       └──────────────────────────────────┘
├─────────────┤   acción y VACÍA la pila           ▲ cancelar hace array_pop()
│ resolviendo │   a [ comando ] para el            │ (nunca sale de la pila entera:
├─────────────┤   siguiente turno                  │  el nivel "comando" es la base)
│  victoria   │
│  derrota    │
└─────────────┘
```

`BattleState` decide **quién** tiene el turno — casi igual que en `04 · 04 §5.6`, con
`turno_jugador`/`turno_enemigo` sustituyendo a `player_turn`/`enemy_turn`. `menu_pila` decide
**cómo** ese jugador concreto construye su acción, y sólo existe mientras `state ==
BattleState.turno_jugador`. Separar las dos máquinas es lo que evita el enum de veinte valores
(`player_turn_choosing_skill_then_target_then_confirm`...) que aparece si se intenta resolver
todo con un único nivel de estados.

---

## 3. El bucle central

```gml
// ---------------------------------------------------------------------------
// objBattleManager — Create (ronda)
// ---------------------------------------------------------------------------
enum BattleState { intro, turno_jugador, turno_enemigo, resolviendo, victoria, derrota }
enum ModoOrdenTurnos { INICIATIVA, ATB }

modo_orden  = ModoOrdenTurnos.INICIATIVA;   // cambia a .ATB sin tocar el resto (§4.2)
atb_activo  = false;                        // false = modo Espera (§1.2); true = Activo

state       = BattleState.intro;
state_timer = 0;

unidades     = [];              // aliados + enemigos, mezclados (§5.1)
cola         = [];               // orden de la ronda o predicción ATB (§5.2/§5.4)
indice_cola  = 0;
turno_actual = undefined;

menu_pila = [];                  // §5.7 — vacía salvo durante turno_jugador
mapa      = undefined;           // §5.9 — sólo si hay mitad táctica
```

```gml
// ---------------------------------------------------------------------------
// objBattleManager — Step
// ---------------------------------------------------------------------------
state_timer++;

switch (state)
{
    case BattleState.intro:
        if (state_timer > 40) ronda_iniciar();
        break;

    case BattleState.turno_jugador:
        var _resultado = menu_batalla_actualizar(menu_pila, turno_actual, unidades, mapa);
        if (_resultado.accion == "ejecutar")
        {
            accion_ejecutar(turno_actual, _resultado.datos);
            turno_terminar(turno_actual);
            set_state(BattleState.resolviendo);
        }
        break;

    case BattleState.turno_enemigo:
        if (state_timer > 30)
        {
            var _decision = (mapa != undefined)
                ? ia_turno_tactico(turno_actual, mapa, unidades)
                : ia_turno_simple(turno_actual, unidades);
            accion_ejecutar(turno_actual, _decision);
            turno_terminar(turno_actual);
            set_state(BattleState.resolviendo);
        }
        break;

    case BattleState.resolviendo:
        if (state_timer > 30)
        {
            var _fin = batalla_comprobar_fin(unidades);
            if (_fin != "continua") { set_state(_fin == "victoria" ? BattleState.victoria : BattleState.derrota); break; }
            turno_avanzar();
        }
        break;

    case BattleState.victoria:
        if (state_timer > 90) { batalla_repartir_recompensas(unidades); room_goto(global.return_room); }
        break;

    case BattleState.derrota:
        if (state_timer > 90) room_goto(rm_game_over);
        break;
}
```

`accion_ejecutar()`, `turno_terminar()`, `turno_avanzar()`, `ronda_iniciar()` y
`batalla_comprobar_fin()` se definen en §5.8, después de las piezas de las que dependen.

---

## 4. Sistemas clave

### 4.1 Orden de turnos: iniciativa

Se calcula **una vez por ronda**: cada unidad tira `velocidad + variación aleatoria pequeña`
(el mismo patrón `random_range` que ya usa `04 · 04 §5.0` para el daño), se ordena de mayor a
menor con `array_sort()` y se recorre. Volver a tirar cada ronda (en vez de una vez para toda la
batalla) es lo que evita que un enemigo lento quede «bloqueado» siempre al final.

### 4.2 Orden de turnos: ATB

Cada unidad acumula `velocidad × delta_time` en una barra 0-100; la primera en llegar a 100
actúa. Tras actuar, su barra vuelve a 0. La **cola visible** (§1.3) no es magia: es simular hacia
delante cuánto tiempo le falta a cada unidad para llenarse, tomar la mínima, avanzar el reloj
virtual de todas por ese tiempo, anotar a la ganadora y repetir — un pequeño evento discreto, no
una animación.

### 4.3 Selección de objetivo

Tres piezas independientes que se combinan: **candidatos** (filtrar por bando y por tipo de
objetivo de la acción — enemigo único, aliado único, área propia...), **validación de alcance**
(en modo táctico, distancia en celdas; en JRPG clásico, el alcance no aplica) y **cursor**
(recorrer los candidatos con envolvente, igual que una lista corta de `13 · 05 §2.2`, o mover un
cursor libre sobre la rejilla que sólo confirma sobre una celda resaltada).

### 4.4 Habilidades y hechizos desde datos

Una habilidad es una fila de una tabla: coste de MP, tipo de objetivo válido, alcance, y **o
bien** daño base con un tipo (que pasa por `dano_resolver()` de `04 · 32`), **o bien** curación,
**o bien** un efecto de estado que aplica a través de `MotorEfectos.aplicar()` — o cualquier
combinación de las tres. Añadir una habilidad nueva es añadir una entrada al JSON, nunca una
rama de código nueva.

### 4.5 El menú de batalla completo

La pila de §1.5 con sus cuatro niveles, implementada con `array_push`/`array_pop` sobre
contextos `{ tipo, opciones, indice }`. Cada nivel reutiliza la misma función de navegación
(subir/bajar con envolvente, confirmar, retroceder); lo único que cambia entre niveles es de
dónde salen las `opciones`.

### 4.6 Movimiento por coste en rejilla

`alcance_movimiento()` (§5.10) es Dijkstra desde la celda de la unidad, con la cola de prioridad
de `ds_priority_*` que ya usa `GridPonderado.buscar()` — la diferencia es que aquí no hay un
destino fijo: se exploran todas las direcciones y se para de expandir una rama en cuanto su
coste acumulado supera el presupuesto de movimiento de la unidad.

### 4.7 Resaltado, alcance de ataque y línea de tiro

El resaltado es dibujar un rectángulo semitransparente por celda (§5.11), reutilizando
`cell_to_px()` de la `GridPonderado` ya cargada. El alcance de ataque tras moverse (§1.8, «zona
de amenaza») es la unión de un anillo de radio `alcance_ataque` alrededor de cada celda
alcanzable. La línea de tiro es un muestreo célula a célula entre dos puntos conocidos (§5.12),
hermano pequeño del `fov_compute()` de `04 · 05 §5.6`.

### 4.8 Terreno y altura

Dos rejillas paralelas a la de coste: `terreno[fila][col]` (una clave, `"bosque"`,
`"agua"`...) y `altura[fila][col]` (un entero). El terreno aporta el coste de movimiento —que
ya alimenta a `GridPonderado`— y un bono de defensa; la altura aporta un bono de daño/precisión
a quien dispara desde más arriba. Ambas se cargan del mismo JSON que define el nivel.

### 4.9 IA de posicionamiento por utilidad

Por cada celda alcanzable se construye una `OpcionUtil` (de `04 · 31 §8`, sin reescribirla) cuya
puntuación combina «¿queda cerca de mi alcance de ataque ideal?» y «¿tiene cobertura de
terreno?». `elegir_por_utilidad()` (también de `04 · 31 §8`) devuelve la mejor; no hace falta
ningún código de decisión nuevo, sólo las curvas de esta sección.

---

## 5. Código base

### 5.0 Configuración

```gml
// ---------------------------------------------------------------------------
// scr_batalla_config
// ---------------------------------------------------------------------------
#macro INICIATIVA_VARIACION   3        // +/- puntos de azar sobre la velocidad (§5.2)
#macro ATB_VELOCIDAD_BASE     18       // puntos de ATB por segundo, a velocidad 10 (§5.3)
#macro ATB_LISTO              100      // umbral para actuar
#macro CELDA_TACTICA          48       // píxeles por celda de la rejilla táctica (§5.9)
#macro RETARDO_INICIAL_MENU   0.40     // s — igual que 13 · 05 §2.2, un solo valor para todo el juego
#macro INTERVALO_MENU         0.10     // s
```

### 5.1 La unidad de combate

```gml
// ---------------------------------------------------------------------------
// scr_unidad_tactica
// ---------------------------------------------------------------------------
enum EquipoBatalla { JUGADOR, ENEMIGO }

/// @func UnidadTactica(_nombre, _stats, _equipo)
/// @desc Envoltorio de combate para un JRPG por turnos o un SRPG. Cuelga de
///       `Stats` (04 · 04 §5.0) y `EstadoCombate` (04 · 30 §6) SIN tocarlos.
///       Sirve igual como struct suelto (JRPG clásico, sin mapa) o colgado de
///       una instancia real con x/y (modo táctico): la lógica de este
///       documento nunca lee `x`/`y` de GameMaker, sólo `celda_col`/`celda_fila`.
/// @param {String} _nombre
/// @param {Struct} _stats   Una instancia de Stats (04 · 04 §5.0).
/// @param {Real}   _equipo  Un miembro de EquipoBatalla.
function UnidadTactica(_nombre, _stats, _equipo) constructor
{
    nombre = _nombre;
    stats  = _stats;
    equipo = _equipo;

    combate = new EstadoCombate(1, stats.get("hp"));   // 04 · 30 §6 — sin tocar
    combate.efectos = new MotorEfectos(combate);         // 04 · 32 §5.4 — sin tocar
    // Opcionales de 04 · 32, añádelos si tu juego los usa:
    //   combate.armadura     = 10;                    // §5.2
    //   combate.resistencias = { fuego: 1.5 };         // §5.1
    //   combate.escudo       = new Escudo(30, 60, 0.5);// §5.3

    habilidades = [];        // array de ids de global.HABILIDADES_DEF (§5.6)

    // --- Orden de turnos: sólo se usa el campo del modo activo ---
    iniciativa = 0;           // §5.2
    atb        = 0;           // §5.3

    // --- Rejilla táctica: undefined si esta unidad no la usa ---
    celda_col         = undefined;
    celda_fila        = undefined;
    puntos_movimiento = 4;
    alcance_ataque    = 1;    // 1 = cuerpo a cuerpo (celdas ortogonales/diagonales adyacentes)

    ha_actuado = false;       // esta ronda/turno ya actuó (§5.2)
}
```

> 💡 **Por qué `UnidadTactica` no hereda de `EstadoCombate` en vez de colgarlo.** Un jugador o
> un enemigo probablemente ya tienen `combate = new EstadoCombate(...)` de `04 · 30`. Colgar
> `UnidadTactica` como una capa aparte (`turno = new UnidadTactica(...)`) en vez de fusionarla
> deja intacto cualquier código que ya lea `combate.vida` directamente — el mismo principio
> aditivo de `04 · 32 §2.1`.

### 5.2 Iniciativa: ordenar la ronda

```gml
// ---------------------------------------------------------------------------
// scr_orden_turnos — parte 1: iniciativa
// ---------------------------------------------------------------------------

/// @func iniciativa_ordenar(_unidades)
/// @desc Tira iniciativa para cada unidad VIVA y devuelve un array nuevo,
///       ordenado de mayor a menor. Llámala al empezar cada ronda: volver a
///       tirar (en vez de fijar el orden para toda la batalla) evita que una
///       unidad lenta quede sistemáticamente última.
/// @param {Array<Struct>} _unidades
/// @returns {Array<Struct>}
function iniciativa_ordenar(_unidades)
{
    var _vivas = [];
    for (var i = 0; i < array_length(_unidades); i++)
    {
        if (_unidades[i].combate.vida <= 0) continue;
        _unidades[i].iniciativa = _unidades[i].stats.get("speed")
                                 + random_range(-INICIATIVA_VARIACION, INICIATIVA_VARIACION);
        array_push(_vivas, _unidades[i]);
    }

    // Descendente: la iniciativa más alta va primero. sign() evita el fallo
    // que documenta el propio manual de array_sort con diferencias < 1.
    array_sort(_vivas, function(_a, _b) { return sign(_b.iniciativa - _a.iniciativa); });
    return _vivas;
}
```

### 5.3 ATB: la barra que se llena

```gml
// ---------------------------------------------------------------------------
// scr_orden_turnos — parte 2: ATB
// ---------------------------------------------------------------------------

/// @func atb_actualizar(_unidades, _congelado)
/// @desc Un paso de todas las barras ATB. Llámala en el Step del
///       objBattleManager. `_congelado` es el modo Espera (§1.2): con el menú
///       abierto, nadie rellena su barra.
/// @param {Array<Struct>} _unidades
/// @param {Bool}          _congelado
function atb_actualizar(_unidades, _congelado)
{
    if (_congelado) return;

    var _dt = delta_time / 1000000;   // microsegundos → segundos (13 · 05 §2.2)
    for (var i = 0; i < array_length(_unidades); i++)
    {
        var _u = _unidades[i];
        if (_u.combate.vida <= 0 || _u.ha_actuado) continue;

        var _vel = _u.stats.get("speed");
        _u.atb = min(ATB_LISTO, _u.atb + (ATB_VELOCIDAD_BASE * _vel / 10) * _dt);
    }
}

/// @func atb_siguiente_lista(_unidades)
/// @desc La primera unidad viva con la barra llena, o undefined si ninguna.
///       Si varias llegan el mismo frame, gana la de mayor velocidad — un
///       desempate legible, no el orden del array.
/// @returns {Struct|Undefined}
function atb_siguiente_lista(_unidades)
{
    var _mejor = undefined;
    for (var i = 0; i < array_length(_unidades); i++)
    {
        var _u = _unidades[i];
        if (_u.combate.vida <= 0) continue;
        if (_u.atb < ATB_LISTO) continue;
        if (_mejor == undefined || _u.stats.get("speed") > _mejor.stats.get("speed")) _mejor = _u;
    }
    return _mejor;
}
```

### 5.4 Cola de turnos visible

```gml
// ---------------------------------------------------------------------------
// scr_orden_turnos — parte 3: la cola que ve el jugador
// ---------------------------------------------------------------------------

/// @func atb_predecir_cola(_unidades, _n)
/// @desc Simula hacia delante quién actuará en los próximos `_n` turnos, sin
///       tocar el estado real: copia el ATB de cada unidad, adelanta el
///       "reloj virtual" hasta que alguien llegue a 100, la anota, la resetea
///       a 0 en la copia, y repite. Es un evento discreto, no una animación:
///       coste O(_n × unidades), trivial incluso con `_n = 8`.
/// @param {Array<Struct>} _unidades
/// @param {Real}          _n
/// @returns {Array<Struct>}
function atb_predecir_cola(_unidades, _n)
{
    var _cant = array_length(_unidades);
    var _copia = array_create(_cant);
    for (var i = 0; i < _cant; i++) _copia[i] = _unidades[i].atb;

    var _cola = [];
    for (var _paso = 0; _paso < _n; _paso++)
    {
        var _mejor_i = -1, _mejor_t = infinity;

        for (var i = 0; i < _cant; i++)
        {
            if (_unidades[i].combate.vida <= 0) continue;
            var _vel = max(_unidades[i].stats.get("speed"), 0.01);
            var _t = (ATB_LISTO - _copia[i]) / _vel;
            if (_t < _mejor_t) { _mejor_t = _t; _mejor_i = i; }
        }
        if (_mejor_i == -1) break;   // nadie vivo: no hay más cola que predecir

        for (var i = 0; i < _cant; i++)
        {
            if (_unidades[i].combate.vida <= 0) continue;
            _copia[i] += max(_unidades[i].stats.get("speed"), 0.01) * _mejor_t;
        }
        array_push(_cola, _unidades[_mejor_i]);
        _copia[_mejor_i] = 0;
    }
    return _cola;
}

/// @func cola_dibujar(_cola, _px, _py, _paso_x)
/// @desc Tira de retratos en Draw GUI: uno por elemento de la cola, atenuado
///       si es del bando enemigo. Sustituye spr_retrato_generico por el
///       retrato real de cada unidad si lo tienes.
function cola_dibujar(_cola, _px, _py, _paso_x)
{
    for (var i = 0; i < array_length(_cola); i++)
    {
        var _u = _cola[i];
        var _x = _px + i * _paso_x;
        var _color = (_u.equipo == EquipoBatalla.JUGADOR) ? c_white : c_red;

        draw_set_alpha(1 - (i * 0.08));   // se desvanece cuanto más lejos en el futuro
        draw_sprite_ext(spr_retrato_generico, 0, _x, _py, 1, 1, 0, _color, 1);
    }
    draw_set_alpha(1);
}
```

> 🔺 **La cola de iniciativa no necesita predicción: ya ES la cola.** `iniciativa_ordenar()`
> devuelve el orden completo de la ronda de una vez; dibújala entera con `cola_dibujar()`
> directamente. `atb_predecir_cola()` sólo hace falta en modo ATB, donde el orden no está fijado
> de antemano.

### 5.5 Selección de objetivo: candidatos, alcance y cursor

```gml
// ---------------------------------------------------------------------------
// scr_objetivo_cursor
// ---------------------------------------------------------------------------

/// @func objetivo_candidatos(_unidades, _lanzador, _tipo_objetivo)
/// @desc Filtra qué unidades son objetivo legal para una acción, por bando.
/// @param {Array<Struct>} _unidades
/// @param {Struct}        _lanzador       Quien ejecuta la acción.
/// @param {String}        _tipo_objetivo  "enemigo_unico" | "aliado_unico" |
///        "enemigos_area" | "aliados_area" | "self"
/// @returns {Array<Struct>}
function objetivo_candidatos(_unidades, _lanzador, _tipo_objetivo)
{
    var _resultado = [];
    for (var i = 0; i < array_length(_unidades); i++)
    {
        var _u = _unidades[i];
        if (_u.combate.vida <= 0) continue;

        var _mismo_equipo = (_u.equipo == _lanzador.equipo);
        switch (_tipo_objetivo)
        {
            case "enemigo_unico":
            case "enemigos_area":
                if (!_mismo_equipo) array_push(_resultado, _u);
                break;
            case "aliado_unico":
            case "aliados_area":
                if (_mismo_equipo) array_push(_resultado, _u);
                break;
            case "self":
                if (_u == _lanzador) array_push(_resultado, _u);
                break;
        }
    }
    return _resultado;
}

/// @func objetivo_en_alcance(_lanzador, _objetivo, _alcance)
/// @desc Validación de distancia en celdas. Si la batalla no usa rejilla
///       (`celda_col` es undefined), el alcance no aplica: todo está "cerca".
/// @param {Struct} _lanzador
/// @param {Struct} _objetivo
/// @param {Real}   _alcance  0 o negativo = sin restricción.
/// @returns {Bool}
function objetivo_en_alcance(_lanzador, _objetivo, _alcance)
{
    if (_alcance <= 0) return true;
    if (_lanzador.celda_col == undefined) return true;   // JRPG clásico, sin rejilla

    var _dc = abs(_lanzador.celda_col  - _objetivo.celda_col);
    var _df = abs(_lanzador.celda_fila - _objetivo.celda_fila);
    return max(_dc, _df) <= _alcance;
}

/// @func objetivo_cursor_mover(_candidatos, _indice, _dir)
/// @desc Cicla el índice del cursor sobre una lista de candidatos, CON
///       envolvente: es una lista corta (13 · 05 §2.2, "lista vertical corta
///       ≤ 8 → sí envuelve" — un grupo de combate rara vez pasa de ahí).
/// @returns {Real} Nuevo índice, siempre dentro de rango.
function objetivo_cursor_mover(_candidatos, _indice, _dir)
{
    var _n = array_length(_candidatos);
    if (_n == 0) return 0;
    return (_indice + _dir + _n) mod _n;
}
```

### 5.6 Habilidades y hechizos desde JSON

```json
// datafiles/habilidades.json
[
  {
    "id": "bola_de_fuego",
    "nombre": "Bola de fuego",
    "coste_mp": 8,
    "tipo_objetivo": "enemigo_unico",
    "alcance": 4,
    "dano_base": 22,
    "tipo_dano": "fuego",
    "efecto_estado": "quemadura_tactica",
    "duracion_efecto": 2
  },
  {
    "id": "curar",
    "nombre": "Curar",
    "coste_mp": 6,
    "tipo_objetivo": "aliado_unico",
    "alcance": 3,
    "curacion_base": 30
  },
  {
    "id": "grito_de_guerra",
    "nombre": "Grito de guerra",
    "coste_mp": 5,
    "tipo_objetivo": "self",
    "alcance": 0,
    "efecto_estado": "regeneracion",
    "duracion_efecto": 3
  }
]
```

```gml
// ---------------------------------------------------------------------------
// scr_habilidades — carga y uso
// ---------------------------------------------------------------------------

/// @func habilidades_cargar(_archivo)
/// @desc Lee habilidades.json con el patrón buffer -> string -> json_parse de
///       04 · 32 §5.1 (resistencias_cargar), no el de 04 · 04 §5.3: es más
///       corto y no necesita leer línea a línea.
/// @param {String} _archivo
function habilidades_cargar(_archivo)
{
    global.HABILIDADES_DEF = {};
    if (!file_exists(_archivo)) return;

    var _buff = buffer_load(_archivo);
    var _json = buffer_read(_buff, buffer_string);
    buffer_delete(_buff);

    var _datos = json_parse(_json);
    for (var i = 0; i < array_length(_datos); i++)
    {
        var _h = _datos[i];
        global.HABILIDADES_DEF[$ _h.id] = _h;
    }
}

/// @func habilidad_obtener(_id)
/// @returns {Struct|Undefined}
function habilidad_obtener(_id)
{
    return variable_struct_exists(global.HABILIDADES_DEF, _id) ? global.HABILIDADES_DEF[$ _id] : undefined;
}

/// @func dano_clave_a_tipo(_clave)
/// @desc La inversa de dano_tipo_a_clave() (04 · 32 §5.1): el JSON guarda el
///       tipo como texto ("fuego"), dano_resolver() lo necesita como DanoTipo.
/// @param {String} _clave
/// @returns {Real} Un miembro de DanoTipo. DanoTipo.FISICO si no reconoce la clave.
function dano_clave_a_tipo(_clave)
{
    switch (_clave)
    {
        case "fisico":  return DanoTipo.FISICO;
        case "fuego":   return DanoTipo.FUEGO;
        case "hielo":   return DanoTipo.HIELO;
        case "rayo":    return DanoTipo.RAYO;
        case "veneno":  return DanoTipo.VENENO;
        case "sagrado": return DanoTipo.SAGRADO;
        case "oscuro":  return DanoTipo.OSCURO;
    }
    return DanoTipo.FISICO;
}

/// @func usar_habilidad(_unidad, _habilidad_id, _objetivos)
/// @desc Gasta el MP y aplica el efecto de la habilidad a cada objetivo. El
///       daño pasa por dano_resolver() de 04 · 32 §5.7 (resistencia, armadura,
///       escudo): esta función NO decide cuánto duele de verdad, sólo el
///       daño BRUTO antes del pipeline.
/// @param {Struct}        _unidad
/// @param {String}        _habilidad_id
/// @param {Array<Struct>} _objetivos
/// @returns {Bool} false si no había MP suficiente o la habilidad no existe.
function usar_habilidad(_unidad, _habilidad_id, _objetivos)
{
    var _def = habilidad_obtener(_habilidad_id);
    if (_def == undefined)
    {
        show_debug_message($"[habilidad] '{_habilidad_id}' no existe — revisa habilidades.json");
        return false;
    }
    if (_unidad.stats.mp < _def.coste_mp) return false;

    _unidad.stats.mp -= _def.coste_mp;

    for (var i = 0; i < array_length(_objetivos); i++)
    {
        var _obj = _objetivos[i];

        if (variable_struct_exists(_def, "dano_base"))
        {
            var _tipo  = variable_struct_exists(_def, "tipo_dano") ? dano_clave_a_tipo(_def.tipo_dano) : DanoTipo.FISICO;
            var _bruto = max(1, round(_def.dano_base + _unidad.stats.get("attack") * 0.3));
            var _final = dano_resolver(_bruto, _tipo, 0, _obj.combate);   // 04 · 32 §5.7 — sin tocar
            _obj.combate.vida = max(0, _obj.combate.vida - _final);
        }

        if (variable_struct_exists(_def, "curacion_base"))
        {
            _obj.combate.curar(_def.curacion_base);   // 04 · 30 §6 — sin tocar
        }

        if (variable_struct_exists(_def, "efecto_estado"))
        {
            var _duracion = variable_struct_exists(_def, "duracion_efecto") ? _def.duracion_efecto : 1;
            _obj.combate.efectos.aplicar(_def.efecto_estado, _duracion);   // 04 · 32 §5.4 — sin tocar
        }
    }
    return true;
}
```

> 🔺 **El motor de efectos de `04 · 32` cuenta "frames"; en turnos, un `tick()` es un turno.**
> `MotorEfectos.tick()` (04 · 32 §5.4) simplemente descuenta un contador cada vez que lo llamas
> — no sabe si eso representa 1/60 de segundo o una ronda entera. En combate por turnos, llama
> `combate.efectos.tick()` **una vez al terminar el turno de esa unidad** (§5.8), y define tus
> efectos con `tic_frames: 1` para que un DoT haga su tic cada turno en vez de cada 60 llamadas.
> Esto se añade a la tabla `global.EFECTOS_DEF` de `04 · 32 §5.5` (se amplía, no se sustituye):
>
> ```gml
> // Añadido a global.EFECTOS_DEF — variante de "quemadura" pensada para un
> // tic por TURNO. Coexiste con la de 04 · 32 §5.5, pensada para 60 fps.
> global.EFECTOS_DEF[$ "quemadura_tactica"] = {
>     nombre : "Quemadura", icono : spr_icono_fuego, color : c_orange,
>     politica : PoliticaApilado.RENOVAR, pilas_max : 1, tic_frames : 1,
>     on_tic : function(_combate, _pilas) { _combate.vida = max(0, _combate.vida - 5); }
> };
> ```

### 5.7 El menú de batalla como pila de contextos

```gml
// ---------------------------------------------------------------------------
// scr_menu_batalla
// ---------------------------------------------------------------------------

/// @func menu_contexto_nuevo(_tipo, _opciones, _extra)
/// @param {String} _tipo      "comando" | "habilidades" | "objetos" | "objetivo" | "confirmacion"
/// @param {Array}  _opciones  Lo que se lista en este nivel (strings, structs de habilidad, o unidades).
/// @param {Struct} _extra     Datos que hay que recordar al bajar de nivel (qué comando se eligió...).
function menu_contexto_nuevo(_tipo, _opciones, _extra = {})
{
    return { tipo: _tipo, opciones: _opciones, indice: 0, extra: _extra };
}

/// @func menu_actual(_pila)
function menu_actual(_pila) { return array_last(_pila); }

/// @func menu_entrar(_pila, _ctx)
function menu_entrar(_pila, _ctx) { array_push(_pila, _ctx); }

/// @func menu_retroceder(_pila)
/// @desc Nunca vacía la pila entera: "comando" es la base y siempre queda.
function menu_retroceder(_pila) { if (array_length(_pila) > 1) array_pop(_pila); }

/// @func menu_navegar(_ctx)
/// @desc Sube/baja con envolvente, usando el mismo par retardo/repetición que
///       13 · 05 §2.2 (repeticion_nueva/repeticion_paso — se reutilizan tal
///       cual, no se repite el código aquí). Devuelve la intención del
///       jugador este frame; el BattleManager decide qué hacer con ella.
/// @returns {Struct} { accion: "mover" | "confirmar" | "retroceder" | "ninguna", opcion }
function menu_navegar(_ctx)
{
    var _n = array_length(_ctx.opciones);
    if (_n == 0) return { accion: "ninguna" };

    if (keyboard_check_pressed(vk_down) || gamepad_button_check_pressed(0, gp_padd))
        _ctx.indice = (_ctx.indice + 1) mod _n;
    if (keyboard_check_pressed(vk_up) || gamepad_button_check_pressed(0, gp_padu))
        _ctx.indice = (_ctx.indice + _n - 1) mod _n;

    if (keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(0, gp_face1))
        return { accion: "confirmar", opcion: _ctx.opciones[_ctx.indice] };

    if (keyboard_check_pressed(vk_escape) || gamepad_button_check_pressed(0, gp_face2))
        return { accion: "retroceder" };

    return { accion: "ninguna" };
}

/// @func menu_batalla_actualizar(_pila, _actor, _unidades, _mapa)
/// @desc Un paso de la máquina de menú. Construye el nivel "comando" la
///       primera vez que se llama para un actor nuevo (pila vacía).
/// @returns {Struct} { accion: "ninguna" | "ejecutar", datos }
function menu_batalla_actualizar(_pila, _actor, _unidades, _mapa)
{
    if (array_length(_pila) == 0)
    {
        menu_entrar(_pila, menu_contexto_nuevo("comando", ["Atacar", "Habilidad", "Objeto", "Defender", "Huir"]));
    }

    var _ctx = menu_actual(_pila);
    var _r   = menu_navegar(_ctx);

    if (_r.accion == "retroceder") { menu_retroceder(_pila); return { accion: "ninguna" }; }
    if (_r.accion != "confirmar")  return { accion: "ninguna" };

    switch (_ctx.tipo)
    {
        case "comando":
            switch (_r.opcion)
            {
                case "Atacar":
                    var _obj = objetivo_candidatos(_unidades, _actor, "enemigo_unico");
                    menu_entrar(_pila, menu_contexto_nuevo("objetivo", _obj, { modo: "atacar" }));
                    break;

                case "Habilidad":
                    var _lista = [];
                    for (var i = 0; i < array_length(_actor.habilidades); i++)
                    {
                        array_push(_lista, habilidad_obtener(_actor.habilidades[i]));
                    }
                    menu_entrar(_pila, menu_contexto_nuevo("habilidades", _lista));
                    break;

                case "Defender":
                    return { accion: "ejecutar", datos: { modo: "defender" } };

                case "Huir":
                    return { accion: "ejecutar", datos: { modo: "huir" } };
            }
            break;

        case "habilidades":
            var _def = _r.opcion;
            if (_actor.stats.mp < _def.coste_mp)
            {
                aviso_lanzar($"Sin MP para {_def.nombre}", "error");   // 13 · 05 §3.5 a) — mismo patrón
                break;
            }
            var _obj = objetivo_candidatos(_unidades, _actor, _def.tipo_objetivo);
            menu_entrar(_pila, menu_contexto_nuevo("objetivo", _obj, { modo: "habilidad", habilidad: _def }));
            break;

        case "objetivo":
            var _elegido = _r.opcion;
            var _alcance = (_ctx.extra.modo == "habilidad") ? _ctx.extra.habilidad.alcance : _actor.alcance_ataque;
            if (!objetivo_en_alcance(_actor, _elegido, _alcance))
            {
                aviso_lanzar("Fuera de alcance", "error");
                break;
            }
            var _extra = _ctx.extra;
            _extra.objetivo = _elegido;
            menu_entrar(_pila, menu_contexto_nuevo("confirmacion", ["Sí", "No"], _extra));
            break;

        case "confirmacion":
            if (_r.opcion == "No") { menu_retroceder(_pila); break; }
            var _datos = _ctx.extra;
            array_resize(_pila, 1);            // vuelve a [comando] para el siguiente turno
            _pila[0].indice = 0;
            return { accion: "ejecutar", datos: _datos };
    }

    return { accion: "ninguna" };
}
```

> 💡 **`aviso_lanzar()` es el mismo helper de notificaciones de `13 · 05 §3.5 i)`** (*toasts*
> apilados): un objetivo fuera de alcance o una habilidad sin MP suficiente son exactamente el
> caso «insistir en un botón inactivo merece una respuesta» que ya resuelve `boton_actualizar()`
> en `13 · 05 §3.5 a)` — aquí se aplica la misma idea sin repetir el componente completo.

### 5.8 El `BattleManager`: el bucle completo

```gml
// ---------------------------------------------------------------------------
// scr_batalla_manager — las funciones que usa el Step de objBattleManager (§3)
// ---------------------------------------------------------------------------

/// @func ronda_iniciar()
/// @desc Sólo tiene sentido en modo INICIATIVA: calcula el orden de la ronda
///       y arranca con el primero. En modo ATB no hay "ronda": se entra
///       directo a esperar a que alguien llene su barra.
function ronda_iniciar()
{
    with (objBattleManager)
    {
        for (var i = 0; i < array_length(unidades); i++) unidades[i].ha_actuado = false;

        if (modo_orden == ModoOrdenTurnos.INICIATIVA)
        {
            cola        = iniciativa_ordenar(unidades);
            indice_cola = 0;
            turno_avanzar();
        }
        else
        {
            set_state(BattleState.turno_enemigo);   // placeholder: turno_avanzar() decide de verdad
            turno_avanzar();
        }
    }
}

/// @func turno_avanzar()
/// @desc Decide de quién es el siguiente turno y cambia de estado. En
///       INICIATIVA recorre `cola`; si se acaba, empieza una ronda nueva. En
///       ATB, actualiza las barras hasta que alguien llegue a 100.
function turno_avanzar()
{
    with (objBattleManager)
    {
        if (modo_orden == ModoOrdenTurnos.INICIATIVA)
        {
            if (indice_cola >= array_length(cola)) { ronda_iniciar(); return; }
            turno_actual = cola[indice_cola++];
        }
        else
        {
            atb_actualizar(unidades, false);   // false: nadie tiene el menú abierto aún
            var _listo = atb_siguiente_lista(unidades);
            if (_listo == undefined) { set_state(BattleState.resolviendo); return; }   // sigue esperando
            turno_actual = _listo;
            turno_actual.atb = 0;
            cola = atb_predecir_cola(unidades, 6);   // para dibujar la tira de retratos (§5.4)
        }

        menu_pila = [];
        set_state(turno_actual.equipo == EquipoBatalla.JUGADOR
                 ? BattleState.turno_jugador : BattleState.turno_enemigo);
    }
}

/// @func accion_ejecutar(_actor, _datos)
/// @desc Un único punto de entrada para CUALQUIER acción, elegida por menú o
///       por IA: son la misma estructura { modo, objetivo?, habilidad? }.
function accion_ejecutar(_actor, _datos)
{
    switch (_datos.modo)
    {
        case "atacar":
            var _obj = _datos.objetivo;
            var _bruto = max(1, round(_actor.stats.calcular_daño(_actor.stats, _obj.stats)));   // 04 · 04 §5.0
            if (global.mapa_activo != undefined)   // bono de terreno/altura (§5.13), sólo en modo táctico
            {
                _bruto = round(resolver_bono_posicion(_actor, _obj, global.mapa_activo) * _bruto);
            }
            var _final = dano_resolver(_bruto, DanoTipo.FISICO, 0, _obj.combate);   // 04 · 32 §5.7
            _obj.combate.vida = max(0, _obj.combate.vida - _final);
            break;

        case "habilidad":
            usar_habilidad(_actor, _datos.habilidad.id, [_datos.objetivo]);
            break;

        case "defender":
            _actor.stats.mods.defense += 10;   // se limpia en turno_terminar()
            break;

        case "huir":
            if (irandom(1) == 1) room_goto(global.return_room);
            break;
    }
}

/// @func turno_terminar(_actor)
/// @desc Cierra el turno de una unidad: tiquea sus efectos de estado (§5.6)
///       y deshace el bonus temporal de "Defender".
function turno_terminar(_actor)
{
    _actor.combate.efectos.tick();          // 04 · 32 §5.4 — un tick = un turno (§5.6)
    _actor.stats.mods.defense = 0;
    _actor.ha_actuado = true;
}

/// @func batalla_comprobar_fin(_unidades)
/// @returns {String} "victoria" | "derrota" | "continua"
function batalla_comprobar_fin(_unidades)
{
    var _jugador_vivo = false, _enemigo_vivo = false;
    for (var i = 0; i < array_length(_unidades); i++)
    {
        if (_unidades[i].combate.vida <= 0) continue;
        if (_unidades[i].equipo == EquipoBatalla.JUGADOR) _jugador_vivo = true; else _enemigo_vivo = true;
    }
    if (!_enemigo_vivo) return "victoria";
    if (!_jugador_vivo) return "derrota";
    return "continua";
}

/// @func batalla_repartir_recompensas(_unidades)
function batalla_repartir_recompensas(_unidades)
{
    var _xp = 0;
    for (var i = 0; i < array_length(_unidades); i++)
    {
        if (_unidades[i].equipo == EquipoBatalla.ENEMIGO) _xp += _unidades[i].stats.get("hp");   // marcador de posición
    }
    global.progression.add_xp(_xp);   // 04 · 04 §6
}

/// @func ia_turno_simple(_actor, _unidades)
/// @desc IA mínima para el JRPG clásico (sin rejilla): ataca al primer
///       jugador vivo. Sustitúyela por elegir_por_utilidad() de 04 · 31 §8
///       si quieres que decida entre atacar/curar/defender.
function ia_turno_simple(_actor, _unidades)
{
    var _candidatos = objetivo_candidatos(_unidades, _actor, "enemigo_unico");
    if (array_length(_candidatos) == 0) return { modo: "defender" };
    return { modo: "atacar", objetivo: _candidatos[0] };
}
```

---

### 5.9 La rejilla táctica: terreno y altura desde datos

```gml
// ---------------------------------------------------------------------------
// scr_terreno_tactico
// ---------------------------------------------------------------------------

/// Coste de movimiento, bono de defensa y si bloquea la línea de tiro.
/// Una tabla, no un switch: añadir un terreno nuevo es una fila más.
global.TERRENO_DEF = {
    llanura : { coste : 1, bono_defensa : 0.00, bloquea_vision : false },
    bosque  : { coste : 2, bono_defensa : 0.20, bloquea_vision : false },
    colina  : { coste : 2, bono_defensa : 0.10, bloquea_vision : false },
    agua    : { coste : 3, bono_defensa : -0.10, bloquea_vision : false },
    muro    : { coste : -1, bono_defensa : 0.00, bloquea_vision : true }
};
```

```json
// datafiles/mapa_llanura_01.json — 8 columnas x 6 filas, en orden fila a fila
{
  "columnas": 8,
  "filas": 6,
  "terreno": [
    "llanura","llanura","bosque","bosque","llanura","llanura","agua","agua",
    "llanura","colina","colina","llanura","llanura","muro","agua","agua",
    "llanura","colina","llanura","llanura","bosque","muro","muro","llanura",
    "llanura","llanura","llanura","bosque","bosque","llanura","llanura","llanura",
    "agua","agua","llanura","llanura","llanura","llanura","colina","llanura",
    "agua","agua","llanura","llanura","llanura","llanura","llanura","llanura"
  ],
  "altura": [
    0,0,0,0,0,0,0,0,
    0,1,1,0,0,2,0,0,
    0,1,0,0,0,2,2,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,1,0,
    0,0,0,0,0,0,0,0
  ]
}
```

```gml
/// @func mapa_tactico_cargar(_archivo)
/// @desc Carga el mapa de un encuentro: construye una GridPonderado (06 ·
///       scr_grid_pathfinding.gml) con los costes de terreno YA puestos, más
///       dos rejillas paralelas de sólo lectura (terreno, altura) para el
///       resto de este documento. La rejilla de movimiento no vuelve a
///       tocarse tras esto: sólo se consulta.
/// @param {String} _archivo
/// @returns {Struct|Undefined} { grid, terreno, altura, columnas, filas }
function mapa_tactico_cargar(_archivo)
{
    if (!file_exists(_archivo)) return undefined;

    var _buff  = buffer_load(_archivo);
    var _json  = buffer_read(_buff, buffer_string);
    buffer_delete(_buff);
    var _datos = json_parse(_json);

    var _grid = new GridPonderado(CELDA_TACTICA, _datos.columnas * CELDA_TACTICA, _datos.filas * CELDA_TACTICA);
    var _terreno = [];
    var _altura  = [];

    for (var _f = 0; _f < _datos.filas; _f++)
    {
        var _fila_t = [];
        var _fila_a = [];
        for (var _c = 0; _c < _datos.columnas; _c++)
        {
            var _idx   = _f * _datos.columnas + _c;
            var _clave = _datos.terreno[_idx];
            var _def   = variable_struct_exists(global.TERRENO_DEF, _clave)
                       ? global.TERRENO_DEF[$ _clave] : global.TERRENO_DEF.llanura;

            array_push(_fila_t, _clave);
            array_push(_fila_a, _datos.altura[_idx]);

            if (_def.coste < 0) _grid.bloquear(_c, _f); else _grid.set_coste(_c, _f, _def.coste);
        }
        array_push(_terreno, _fila_t);
        array_push(_altura, _fila_a);
    }

    return { grid: _grid, terreno: _terreno, altura: _altura, columnas: _datos.columnas, filas: _datos.filas };
}

/// @func terreno_definicion(_mapa, _col, _fila)
/// @desc Definición de terreno de una celda. Fuera del mapa se trata como un
///       muro: bloquea movimiento y visión, para que ningún cálculo tenga
///       que comprobar los límites dos veces.
/// @returns {Struct}
function terreno_definicion(_mapa, _col, _fila)
{
    if (_col < 0 || _fila < 0 || _col >= _mapa.columnas || _fila >= _mapa.filas)
    {
        return global.TERRENO_DEF.muro;
    }
    var _clave = _mapa.terreno[_fila][_col];
    return variable_struct_exists(global.TERRENO_DEF, _clave) ? global.TERRENO_DEF[$ _clave] : global.TERRENO_DEF.llanura;
}
```

### 5.10 Rango de movimiento: Dijkstra por presupuesto

```gml
// ---------------------------------------------------------------------------
// scr_rejilla_tactica — parte 1: hasta dónde puede llegar una unidad
// ---------------------------------------------------------------------------

/// @func alcance_movimiento(_grid, _col0, _fil0, _presupuesto, _diagonal)
/// @desc Todas las celdas alcanzables desde (_col0,_fil0) gastando como mucho
///       `_presupuesto` puntos de movimiento, sobre una GridPonderado (06 ·
///       scr_grid_pathfinding.gml) que ya tiene los costes de terreno puestos
///       con set_coste()/bloquear() (§5.9). Es Dijkstra, no BFS: con costes
///       uniformes ambos coinciden, pero en cuanto el barro cuesta más que la
///       hierba (§1.6), BFS da resultados incorrectos.
///       Mismo esqueleto que GridPonderado.buscar() (06 · scr_grid_pathfinding.gml),
///       sin destino fijo: se expande en TODAS direcciones y se corta la rama
///       en cuanto se pasa del presupuesto.
/// @param {Struct} _grid          Una GridPonderado ya cargada.
/// @param {Real}   _col0
/// @param {Real}   _fil0
/// @param {Real}   _presupuesto
/// @param {Bool}   _diagonal
/// @returns {Struct} { alcanzables: Array<{col,fila,coste}>, padre: Array<Real> }
///          `padre` es un array plano (índice = fila*columnas+col) con el
///          índice de la celda anterior en la ruta más barata, o -1. Sirve
///          para reconstruir la ruta con reconstruir_ruta() (más abajo).
function alcance_movimiento(_grid, _col0, _fil0, _presupuesto, _diagonal = true)
{
    var _total    = _grid.columnas * _grid.filas;
    var _g        = array_create(_total, -1);
    var _padre    = array_create(_total, -1);
    var _cerrado  = array_create(_total, false);
    var _abiertos = ds_priority_create();

    var _inicio = _fil0 * _grid.columnas + _col0;
    _g[_inicio] = 0;
    ds_priority_add(_abiertos, _inicio, 0);

    var _dc = [ 1, -1,  0,  0,  1,  1, -1, -1 ];
    var _df = [ 0,  0,  1, -1,  1, -1,  1, -1 ];
    var _max_vecinos = _diagonal ? 8 : 4;

    var _alcanzables = [];

    while (!ds_priority_empty(_abiertos))
    {
        var _actual = ds_priority_delete_min(_abiertos);
        if (_cerrado[_actual]) continue;
        _cerrado[_actual] = true;

        var _col_a = _actual mod _grid.columnas;
        var _fil_a = _actual div _grid.columnas;
        array_push(_alcanzables, { col: _col_a, fila: _fil_a, coste: _g[_actual] });

        for (var i = 0; i < _max_vecinos; i++)
        {
            var _cv = _col_a + _dc[i];
            var _fv = _fil_a + _df[i];
            if (_cv < 0 || _fv < 0 || _cv >= _grid.columnas || _fv >= _grid.filas) continue;

            var _iv = _fv * _grid.columnas + _cv;
            if (_cerrado[_iv]) continue;

            var _coste_celda = _grid.get_coste(_cv, _fv);
            if (_coste_celda < 0) continue;   // intransitable (muro, §5.9)

            var _paso    = (i >= 4) ? (_coste_celda * 1.4142) : _coste_celda;
            var _nuevo_g = _g[_actual] + _paso;
            if (_nuevo_g > _presupuesto) continue;   // se acaba el presupuesto: no se expande

            if (_g[_iv] == -1 || _nuevo_g < _g[_iv])
            {
                _g[_iv]     = _nuevo_g;
                _padre[_iv] = _actual;
                ds_priority_add(_abiertos, _iv, _nuevo_g);
            }
        }
    }

    ds_priority_destroy(_abiertos);
    return { alcanzables: _alcanzables, padre: _padre };
}

/// @func reconstruir_ruta(_padre, _grid, _col_destino, _fil_destino)
/// @desc Reconstruye la ruta más barata hasta una celda, a partir del
///       `padre` que devuelve alcance_movimiento(). Para dibujar el camino
///       bajo el cursor antes de confirmar el movimiento.
/// @returns {Array<Struct>} [{col,fila}, ...] del origen al destino.
function reconstruir_ruta(_padre, _grid, _col_destino, _fil_destino)
{
    var _invertida = [];
    var _nodo = _fil_destino * _grid.columnas + _col_destino;
    while (_nodo != -1)
    {
        array_push(_invertida, { col: _nodo mod _grid.columnas, fila: _nodo div _grid.columnas });
        _nodo = _padre[_nodo];
    }

    var _ruta = [];
    for (var i = array_length(_invertida) - 1; i >= 0; i--) array_push(_ruta, _invertida[i]);
    return _ruta;
}
```

### 5.11 Resaltar casillas: movimiento, ataque y ruta

```gml
// ---------------------------------------------------------------------------
// scr_rejilla_tactica — parte 2: dibujar
// ---------------------------------------------------------------------------

/// @func celdas_en_rango(_grid, _alcanzables, _rango, _diagonal)
/// @desc La "zona de amenaza" de §1.8: la unión del alcance de ataque
///       alrededor de CADA celda a la que la unidad podría moverse. Es lo
///       que enseña al jugador dónde es seguro pisar.
/// @param {Struct}        _grid
/// @param {Array<Struct>} _alcanzables  El resultado de alcance_movimiento().alcanzables
/// @param {Real}          _rango
/// @param {Bool}          _diagonal
/// @returns {Array<Struct>} [{col,fila}, ...] sin duplicados.
function celdas_en_rango(_grid, _alcanzables, _rango, _diagonal = true)
{
    var _total    = _grid.columnas * _grid.filas;
    var _marcado  = array_create(_total, false);
    var _resultado = [];

    for (var i = 0; i < array_length(_alcanzables); i++)
    {
        var _oc = _alcanzables[i].col;
        var _of = _alcanzables[i].fila;

        for (var _df2 = -_rango; _df2 <= _rango; _df2++)
        {
            for (var _dc2 = -_rango; _dc2 <= _rango; _dc2++)
            {
                var _dist = _diagonal ? max(abs(_dc2), abs(_df2)) : (abs(_dc2) + abs(_df2));
                if (_dist == 0 || _dist > _rango) continue;

                var _cc = _oc + _dc2, _cf = _of + _df2;
                if (_cc < 0 || _cf < 0 || _cc >= _grid.columnas || _cf >= _grid.filas) continue;

                var _idx = _cf * _grid.columnas + _cc;
                if (_marcado[_idx]) continue;
                _marcado[_idx] = true;
                array_push(_resultado, { col: _cc, fila: _cf });
            }
        }
    }
    return _resultado;
}

/// @func resaltar_celdas(_grid, _celdas, _color, _alfa)
/// @desc Un rectángulo semitransparente por celda. Llámalo en un evento Draw
///       (no en Draw GUI: la rejilla vive en coordenadas del mundo).
function resaltar_celdas(_grid, _celdas, _color, _alfa = 0.35)
{
    var _c_previo = draw_get_color();
    var _a_previo = draw_get_alpha();
    draw_set_color(_color);
    draw_set_alpha(_alfa);

    var _mitad = _grid.celda * 0.5;
    for (var i = 0; i < array_length(_celdas); i++)
    {
        var _p = _grid.cell_to_px(_celdas[i].col, _celdas[i].fila);   // 06 · scr_grid_pathfinding.gml
        draw_rectangle(_p.x - _mitad, _p.y - _mitad, _p.x + _mitad - 1, _p.y + _mitad - 1, false);
    }
    draw_set_color(_c_previo);
    draw_set_alpha(_a_previo);
}
```

```gml
// obj_cursor_tactico — Draw, mientras se elige destino de movimiento
resaltar_celdas(mapa.grid, alcanzables_actuales, c_aqua, 0.30);     // azul: puede moverse aquí
resaltar_celdas(mapa.grid, amenaza_actual,        c_red,  0.20);     // rojo: y desde ahí, atacar aquí

if (hay_celda_bajo_cursor)
{
    var _ruta = reconstruir_ruta(padre_actual, mapa.grid, cursor_col, cursor_fila);
    resaltar_celdas(mapa.grid, _ruta, c_yellow, 0.45);              // amarillo: la ruta concreta
}
```

### 5.12 Línea de tiro en rejilla

```gml
// ---------------------------------------------------------------------------
// scr_rejilla_tactica — parte 3: ¿hay algo en medio?
// ---------------------------------------------------------------------------

/// @func linea_de_tiro(_mapa, _c1, _f1, _c2, _f2)
/// @desc Recorre la rejilla célula a célula entre dos puntos CONOCIDOS —
///       hermano pequeño del fov_compute() de 04 · 05 §5.6, que barre 360°
///       porque no conoce el destino de antemano. Con 4 muestras por celda
///       no se cuela por la esquina de un muro en diagonal.
///       Aquí `round()` es correcto, no una trampa: la advertencia de
///       "siempre floor, nunca round" de 13 · 13 §7.1 es sobre convertir
///       PÍXELES del mundo a celda (donde las coordenadas negativas rompen
///       round()); esto interpola entre dos celdas ya no negativas.
/// @param {Struct} _mapa  El struct de mapa_tactico_cargar() (§5.9).
/// @returns {Bool}
function linea_de_tiro(_mapa, _c1, _f1, _c2, _f2)
{
    var _dx = _c2 - _c1;
    var _dy = _f2 - _f1;
    var _pasos = max(abs(_dx), abs(_dy)) * 4;
    if (_pasos == 0) return true;

    for (var i = 1; i < _pasos; i++)
    {
        var _t  = i / _pasos;
        var _cx = round(_c1 + _dx * _t);
        var _cy = round(_f1 + _dy * _t);

        // El origen y el destino nunca bloquean su propia línea, aunque
        // tengan cobertura (un arquero SÍ ve a través de su propio bosque).
        if ((_cx == _c1 && _cy == _f1) || (_cx == _c2 && _cy == _f2)) continue;

        if (terreno_definicion(_mapa, _cx, _cy).bloquea_vision) return false;
    }
    return true;
}
```

### 5.13 Resolver un ataque táctico: terreno y altura

```gml
// ---------------------------------------------------------------------------
// scr_rejilla_tactica — parte 4: el bono de posición
// ---------------------------------------------------------------------------

/// @func resolver_bono_posicion(_atacante, _objetivo, _mapa)
/// @desc Multiplicador que se aplica al daño BRUTO, ANTES de dano_resolver()
///       (04 · 32 §1.1, capa 1: es un multiplicador más del daño base, como
///       el crítico o el escalado de combo — NO toca resistencia/armadura/
///       escudo, esas siguen siendo capas 2-4, intactas).
/// ⚠️ Los coeficientes (10 % por nivel de altura, tope 30 %; la cobertura de
///    §5.9) son una convención de género razonable, no una cifra medida en
///    ningún juego concreto: ajústalos con el panel de balance de
///    13 · 01 §9.4.
/// @param {Struct} _atacante  UnidadTactica.
/// @param {Struct} _objetivo  UnidadTactica.
/// @param {Struct} _mapa
/// @returns {Real}  1.0 = sin cambios.
function resolver_bono_posicion(_atacante, _objetivo, _mapa)
{
    var _h_atacante = _mapa.altura[_atacante.celda_fila][_atacante.celda_col];
    var _h_objetivo = _mapa.altura[_objetivo.celda_fila][_objetivo.celda_col];
    var _bono_altura = 1 + clamp((_h_atacante - _h_objetivo) * 0.10, 0, 0.30);

    var _cobertura = terreno_definicion(_mapa, _objetivo.celda_col, _objetivo.celda_fila).bono_defensa;

    return _bono_altura * (1 - clamp(_cobertura, -0.5, 0.5));
}
```

### 5.14 IA de posicionamiento por utilidad

```gml
// ---------------------------------------------------------------------------
// scr_ia_posicionamiento
// ---------------------------------------------------------------------------

/// @func ia_elegir_celda_destino(_unidad, _alcanzables, _enemigos, _mapa)
/// @desc Puntúa cada celda alcanzable y elige la mejor con
///       elegir_por_utilidad() (04 · 31 §8, SIN reescribirla). Aquí sólo van
///       las consideraciones NUEVAS, propias de posicionamiento:
///         1. Alcance ideal: mejor cuanto más cerca del alcance de ataque de
///            la unidad, sin pasarse (para un arquero, ni pegado al enemigo
///            ni fuera de tiro).
///         2. Cobertura de terreno de esa celda.
///       Cada OpcionUtil usa method() para atar sus propios datos (la celda,
///       la unidad, los enemigos) como `self`: 04 · 32 §5.6 hace lo mismo con
///       tiene_control(). Es DELIBERADO no capturar `_c` por closure: la
///       propia biblioteca (06 · scr_grid_pathfinding.gml) advierte de que
///       las funciones anidadas que capturan variables locales son frágiles
///       en GML.
/// @param {Struct}        _unidad       UnidadTactica que decide.
/// @param {Array<Struct>} _alcanzables  alcance_movimiento(...).alcanzables (§5.10)
/// @param {Array<Struct>} _enemigos     Vivos, del bando contrario.
/// @param {Struct}        _mapa
/// @returns {Struct|Undefined} La OpcionUtil elegida; `.celda` es el destino.
function ia_elegir_celda_destino(_unidad, _alcanzables, _enemigos, _mapa)
{
    var _opciones = [];

    for (var i = 0; i < array_length(_alcanzables); i++)
    {
        var _c = _alcanzables[i];
        var _datos = { celda: _c, unidad: _unidad, enemigos: _enemigos, mapa: _mapa };

        var _puntuar = method(_datos, function(_pizarra)
        {
            var _dist_min = infinity;
            for (var j = 0; j < array_length(enemigos); j++)
            {
                if (enemigos[j].combate.vida <= 0) continue;
                var _d = max(abs(celda.col - enemigos[j].celda_col), abs(celda.fila - enemigos[j].celda_fila));
                _dist_min = min(_dist_min, _d);
            }
            if (_dist_min == infinity) return 0;   // no queda nadie vivo a quien acercarse

            var _en_rango_ideal = 1 - curva_lineal(abs(_dist_min - unidad.alcance_ataque), 3);   // 04 · 31 §8
            var _cobertura      = curva_lineal(terreno_definicion(mapa, celda.col, celda.fila).bono_defensa, 0.3);

            return clamp(_en_rango_ideal * 0.7 + _cobertura * 0.3, 0, 1);
        });

        var _opcion = new OpcionUtil($"mover_{_c.col}_{_c.fila}", _puntuar, undefined);
        _opcion.celda = _c;   // el tercer argumento de OpcionUtil no hace falta: sólo pedimos
                              // la MEJOR celda, no ejecutamos un nodo de árbol de comportamiento.
        array_push(_opciones, _opcion);
    }

    return elegir_por_utilidad(_opciones, {}, 0.05, 0.10);   // 04 · 31 §8 — sin reescribir
}

/// @func ia_turno_tactico(_actor, _mapa, _unidades)
/// @desc El turno completo de un enemigo en modo táctico: elegir dónde
///       moverse (utilidad, arriba) y a quién atacar desde ahí (el primero
///       en alcance y con línea de tiro libre). Devuelve la misma forma
///       { modo, objetivo } que consume accion_ejecutar() (§5.8), más el
///       movimiento ya aplicado a `_actor.celda_col/fila`.
/// @returns {Struct}
function ia_turno_tactico(_actor, _mapa, _unidades)
{
    var _enemigos = objetivo_candidatos(_unidades, _actor, "enemigo_unico");

    var _alcance = alcance_movimiento(_mapa.grid, _actor.celda_col, _actor.celda_fila, _actor.puntos_movimiento);
    var _destino = ia_elegir_celda_destino(_actor, _alcance.alcanzables, _enemigos, _mapa);

    if (_destino != undefined)
    {
        _actor.celda_col  = _destino.celda.col;
        _actor.celda_fila = _destino.celda.fila;
    }

    for (var i = 0; i < array_length(_enemigos); i++)
    {
        var _obj = _enemigos[i];
        if (!objetivo_en_alcance(_actor, _obj, _actor.alcance_ataque)) continue;
        if (!linea_de_tiro(_mapa, _actor.celda_col, _actor.celda_fila, _obj.celda_col, _obj.celda_fila)) continue;
        return { modo: "atacar", objetivo: _obj };
    }

    return { modo: "defender" };   // se movió, pero nadie quedó a tiro
}
```

---

## 6. Gestión del estado: lo que se añade

```gml
// ---------------------------------------------------------------------------
// obj_batalla_persistente — Create, junto al resto de 04 · 04 §6
// ---------------------------------------------------------------------------
habilidades_cargar("habilidades.json");         // §5.6 — una vez, al arrancar el juego

// Al ENTRAR en un combate concreto (no persistente: se reconstruye cada vez)
global.mapa_activo = mapa_tactico_cargar("mapa_llanura_01.json");   // undefined si no hay rejilla
```

```gml
/// @func UnidadTactica.serializar()
/// @desc Añádelo junto al resto: guarda lo que sobrevive a una recarga
///       (vida, MP, posición); la iniciativa/ATB y la pila de menú NO se
///       guardan — igual que 04 · 32 §5.12 no guarda las inmunidades, un
///       combate a medias no se recarga desde disco, se abandona o se pierde.
serializar = function()
{
    return {
        nombre: nombre, equipo: equipo,
        stats: stats.serialize(),                    // 04 · 04 §5.0
        vida: combate.vida, vida_max: combate.vida_max,
        efectos: combate.efectos.serializar(),        // 04 · 32 §5.4
        celda_col: celda_col, celda_fila: celda_fila
    };
};
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Arreglo |
|---|---|---|
| Recalcular la iniciativa cada frame en vez de una vez por ronda | El orden "tiembla": una unidad cambia de puesto a mitad de su propio turno | Llama `iniciativa_ordenar()` sólo en `ronda_iniciar()`, nunca en el `Step` |
| ATB en modo Activo por defecto | El jugador muere eligiendo qué hacer, sin haber tenido tiempo de decidir | Empieza en modo Espera (`atb_activo = false`, congela `atb_actualizar()` mientras `state == turno_jugador`); ofrece Activo como opción, no como default |
| `menu_pila` nunca queda vacía del todo tras confirmar | El siguiente turno hereda submenús del anterior; el cursor aparece donde no debería | `array_resize(_pila, 1)` al confirmar (§5.7, caso `"confirmacion"`), no `menu_retroceder()` repetido |
| BFS en vez de Dijkstra con terreno de coste variable | Una unidad "alcanza" una casilla de agua (coste 3) que en realidad está fuera de su presupuesto | Usa `alcance_movimiento()` (§5.10), que compara coste ACUMULADO contra el presupuesto, no número de pasos |
| Ignorar la diagonal más cara en el presupuesto de movimiento | Las unidades recorren más "distancia real" en diagonal de la que deberían poder | El `1.4142` de §5.10 (igual que `GridPonderado.buscar()`) penaliza la diagonal; no lo quites "para simplificar" |
| Línea de tiro que no excluye origen/destino | Un arquero dentro de su propio bosque no puede dispararse ni a los pies | `linea_de_tiro()` (§5.12) salta explícitamente la celda de origen y la de destino |
| Aplicar el bono de altura/terreno DESPUÉS de `dano_resolver()` | La resistencia elemental y la armadura ya redujeron el número; multiplicar después da un daño final incoherente con la tabla de resistencias | El bono de posición multiplica el `_bruto`, ANTES de `dano_resolver()` (§5.13, respeta el pipeline de capas de `04 · 32 §1.1`) |
| Duración de un efecto de estado en "frames" dentro de un combate por turnos | El veneno "nunca hace tic": con `tic_frames: 60` y un `tick()` por turno, hacen falta 60 turnos | Añade variantes con `tic_frames: 1` a `global.EFECTOS_DEF` (§5.6), no reutilices las de `04 · 32 §5.5` tal cual |
| Cerrar sobre la variable de bucle en la IA de posicionamiento | Todas las `OpcionUtil` puntúan la ÚLTIMA celda del bucle, no la suya | Usa `method(_datos, function(){...})` con un struct NUEVO por iteración (§5.14), nunca una función anidada que lea `_c` directamente |
| No destruir el `ds_priority` si la función corta antes de vaciarlo | Fuga de memoria en cada cálculo de rango de movimiento | `ds_priority_destroy(_abiertos)` corre siempre, incluso si el bucle termina por presupuesto agotado, no sólo por cola vacía (§5.10 ya lo hace: revísalo si lo adaptas) |

---

## 8. Cómo escalarlo

1. **Precisión y esquiva** — una probabilidad de acierto (`13 · 13 §5.1`–`§5.4`, distribuciones)
   sobre el ataque, con el bono de terreno de §5.9 restando a la evasión del objetivo en vez de
   sólo a su defensa. Es el paso natural tras esto: Fire Emblem lo trata como el segundo eje de
   decisión después de la posición.
2. **Peso y desplazamiento como mecánica** — en vez de sólo dañar, un ataque puede empujar al
   objetivo N celdas (comprobando colisión contra terreno intransitable y otras unidades),
   convirtiendo el posicionamiento en el objetivo del combate en sí — la lección de
   *Into the Breach*.
3. **Interacción entre bandos aliado/NPC** — `04 · 04 §1` ya asume dos bandos; añadir un tercero
   (aliados controlados por IA que no obedecen órdenes directas) reutiliza `EquipoBatalla` con
   un valor más y la IA de utilidad de §5.14 sin tocar el resto.
4. **Guardar partidas a mitad de una campaña táctica** — persiste qué unidades sobrevivieron y su
   progresión entre mapas, con el patrón de `01 · 14` y `04 · 04 §5.8`; el estado de un combate
   EN CURSO sigue sin guardarse (§6).
5. **Habilidades con múltiples objetivos por prioridad** — un hechizo que golpea "al enemigo con
   menos vida" en vez de a uno elegido a mano es una `OpcionUtil` más sobre la lista de
   candidatos de §5.5, no un sistema nuevo.
6. **Cuándo pasar a `04 · 36`**: en cuanto el juego necesite habilidades con enfriamiento real
   entre combates (no sólo "una vez por turno"), cargas acumulables, o un árbol de progresión de
   habilidades — la mitad de datos (`habilidades.json`) se comparte tal cual entre los dos
   documentos.
7. **Cuándo pasar a `04 · 33`**: cuando los enemigos necesiten arquetipos con ficha propia,
   tabla de amenaza (*aggro*) o un director de intensidad que decida qué oleada mandar — la IA
   de posicionamiento de §5.14 sigue siendo la pieza de "dónde", el director decide "cuándo" y
   "con qué".

---

## Ver también

- [04 · 04 — RPG / Action RPG](./04%20-%20RPG%20_%20Action%20RPG.md) — `Stats`, `calcular_daño()`
  y el `BattleManager` mínimo (§5.6) al que este documento sustituye como referencia.
- [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  `EstadoCombate`, `MotorEfectos`, `dano_resolver()` y el pipeline de capas que este documento
  reutiliza sin reescribir.
- [04 · 36 — Habilidades, enfriamientos y recursos de combate](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md) —
  el gestor completo de habilidades en tiempo real (enfriamiento, cargas, árbol de progresión);
  comparte el formato de `habilidades.json` con §5.6 de este documento.
- [04 · 31 — IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md) —
  `curva_lineal()`, `OpcionUtil` y `elegir_por_utilidad()`, la base de la IA de posicionamiento
  de §5.14.
- [04 · 33 — Diseño de enemigos, encuentros y director de combate](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) —
  arquetipos, tabla de amenaza y director de intensidad: la capa de diseño de encuentro por
  encima de este documento.
- [04 · 18 — Menús con scroll y navegación](./18%20-%20Menús%20con%20scroll%20y%20navegación.md) —
  `menu_mover()`, la navegación de listas de la que la pila de §5.7 toma el patrón de foco.
- [04 · 05 — Roguelike y generación procedural §5.6](./05%20-%20Roguelike%20y%20generación%20procedural.md) —
  `fov_compute()`, el raycasting de campo de visión del que `linea_de_tiro()` (§5.12) es una
  versión de un solo segmento.
- [06 · `scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml) —
  `GridPonderado`, reutilizada tal cual para el coste de movimiento y el A* que `alcance_movimiento()`
  (§5.10) extiende con un presupuesto en vez de un destino fijo.
- [13 · 05 — UI y UX de juego §2.2 y §3.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md) —
  las cinco leyes del foco, la envolvente, la repetición de input y el patrón de botón con
  cuatro estados sobre los que se construye el menú de batalla de §5.7.
- [13 · 13 — Matemáticas aplicadas al juego §7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
  mundo↔celda, *snapping* e isométrico/hexágonos: la base de coordenadas de rejilla de la que
  `linea_de_tiro()` toma la advertencia de `floor` frente a `round`.
- [13 · 01 — Diseño de juego: core loop, mecánicas, balance y dificultad §4.4 y §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md) —
  TTK, el panel de balance en caliente al que apuntan los ⚠️ de §5.13.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) —
  el patrón `buffer_load`/`json_parse` que usan `habilidades_cargar()` y `mapa_tactico_cargar()`.

---

## 9. Fuentes

**Diseño y convenciones de fuera de GameMaker** (consultadas el 2026-09-06):

- **Active Time Battle**, Wikipedia — origen del sistema ATB en *Final Fantasy IV* (1991),
  diseñado por Hiroyuki Ito a partir de una analogía con la Fórmula 1 (un coche más rápido
  completa más vueltas), la diferencia entre modo Activo y modo Espera, y la vigencia de la
  patente (1995-2010) —
  https://en.wikipedia.org/wiki/Active_Time_Battle
- **Fire Emblem (video game)**, Wikipedia — el triángulo de armas, el terreno como variable de
  combate (bosque, fortaleza) y el orden de turnos por bandos (jugador, enemigo, aliado NPC) —
  https://en.wikipedia.org/wiki/Fire_Emblem_(video_game)
- **Into the Breach**, Wikipedia — la información perfecta (mostrar la intención del enemigo
  antes de que actúe), el empuje/desplazamiento como mecánica central y la rejilla de 8×8 —
  https://en.wikipedia.org/wiki/Into_the_Breach
- ⚠️ *Game AI Pro* (varios autores, ed. Steve Rabin) sobre *tactical position selection* e
  *influence maps* como marco para IA de posicionamiento, y *Designing Games* de Tynan
  Sylvester sobre decisiones significativas: ambos ya citados y no reabiertos en esta sesión —
  se referencian como criterio de diseño consolidado, no como cifra verificada; ver la misma
  advertencia en `04 · 31` y `04 · 32`.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`; todos los
símbolos de GML de este documento comprobados con `_indice/buscar.py` contra el runtime
`2026.0.0.23`):

- `ds_priority_create`/`ds_priority_add`/`ds_priority_delete_min`/`ds_priority_empty`/
  `ds_priority_destroy` — familia *DS Priority Queues*, ya en uso en
  [06 · `scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml).
- `array_sort`, `array_pop`, `array_last`, `array_resize`, `array_create`, `array_copy` —
  familia *Variable Functions*, usadas para el orden de iniciativa (§5.2) y la pila de menú
  (§5.7).
- `method()` — para atar datos propios a cada `OpcionUtil` de la IA de posicionamiento (§5.14),
  el mismo patrón que `04 · 32 §5.6` usa para `tiene_control()`.
- `buffer_load`/`buffer_read`/`buffer_delete`/`json_parse` — el patrón de lectura de JSON de
  [01 · 14 §8](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md), reutilizado tal
  cual en `habilidades_cargar()` y `mapa_tactico_cargar()` (§5.6, §5.9).
- `keyboard_check_pressed`/`gamepad_button_check_pressed`/`vk_up`/`vk_down`/`vk_enter`/
  `vk_escape`/`gp_padu`/`gp_padd`/`gp_face1`/`gp_face2` — familia *Keyboard/Gamepad Input*, para
  la navegación del menú de batalla (§5.7).

> ⚠️ **Lo que NO está verificado en este documento.** Todos los símbolos de GML existen en el
> runtime `2026.0.0.23` (comprobados uno a uno con `buscar.py`), pero el código **no se ha
> compilado en un proyecto real**: `spr_retrato_generico`, `spr_icono_fuego` y el resto de
> sprites son marcadores de posición, igual que en `04 · 30` y `04 · 32`. Los números —variación
> de iniciativa de ±3, velocidad base de ATB, +10 % de daño por nivel de altura, coste 2 del
> bosque— son un punto de partida razonable, no cifras medidas en ningún juego concreto:
> ajústalos con el panel de balance de `13 · 01 §9.4`.
