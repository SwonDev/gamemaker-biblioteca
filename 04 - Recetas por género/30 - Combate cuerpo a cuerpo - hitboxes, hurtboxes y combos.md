# 30 · Combate cuerpo a cuerpo — hitboxes, hurtboxes y combos

> **Dificultad:** alta · **Antes de esto:** una máquina de estados y una animación por
> fotogramas que funcionen.
> El sistema que hay debajo de un beat 'em up, un hack and slash, un action RPG, un
> plataformas con espada y un juego de lucha. Todos comparten la misma pieza: **lo que golpea
> y lo que puede ser golpeado son dos cosas distintas, y ninguna de las dos es la máscara con
> la que el personaje choca contra las paredes.**
>
> **Qué NO cubre este documento** (y dónde está): la *sensación* del golpe —hit stop, sacudida
> de cámara, partículas, flash, texto flotante— vive entera en
> [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md); aquí se **invoca**, no se
> reimplementa. El movimiento y `move_and_collide()` están en
> [01 · 08](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md). La animación,
> el origen del sprite y la tabla mínima de *frame data* están en
> [13 · 04](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md);
> este documento es su continuación natural. La IA que decide *cuándo* atacar está en
> [04 · 23](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md).

---

## 1. Visión general

### 1.1 Tres cajas, no una

El error que arruina más sistemas de combate es usar **una sola caja** para todo. Un personaje
necesita tres, y son independientes:

| Caja | Qué es | Quién la usa | En GameMaker |
|---|---|---|---|
| **Máscara de movimiento** | Con qué choca contra paredes y suelo | `move_and_collide()`, `place_meeting()` | `mask_index` — un sprite fijo, rectangular, a la altura de los pies |
| **Hurtbox** (caja de daño recibido) | Dónde te pueden herir | El sistema de combate | Un rectángulo **en datos**, relativo al origen |
| **Hitbox** (caja de golpe) | Qué hiere | El sistema de combate | Una instancia efímera de `obj_hitbox` |

La definición canónica del vocabulario es la del glosario de Infil, que es la referencia de
facto de la comunidad de juegos de lucha:

> «**Hitbox**: un área predefinida […] que le dice al juego cómo un ataque concreto puede
> entrar en contacto con un personaje. […] Para determinar si un golpe conecta, el juego mira
> si su *hitbox* se solapa con la *hurtbox* del rival.»
>
> «**Hurtbox**: un área predefinida […] que le dice al juego cómo tu personaje puede ser
> golpeado por cualquier ataque entrante.»

Y advierte de la confusión más común, que también verás en foros en español:

> «Mucha gente llama "hitbox" a esto [a la hurtbox] […], lo cual a veces hace difícil
> distinguir entre lo que ataca y lo que es atacado.»

**Por qué se desacoplan del sprite.** Si las cajas son «el sprite» o «la bounding box», pasan
tres cosas malas:

1. La caja crece y mengua con cada fotograma de la animación. Un fotograma con el brazo
   estirado hace al personaje **más fácil de golpear** justo cuando ataca. El jugador lo
   percibe como injusticia y no sabe por qué.
2. `image_xscale` e `image_yscale` **escalan también la máscara**: un *squash & stretch* de
   dos píxeles altera las colisiones. Por eso el squash se aplica en el `Draw`
   ([13 · 04 §3.9](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md)).
3. No puedes tener **un ataque que golpee más lejos que el dibujo** (casi todos los juegos
   buenos lo hacen) ni **una hurtbox más pequeña que el personaje** (casi todos los buenos
   también: perdona errores del jugador).

### 1.2 El vocabulario mínimo: frame data

Todo el diseño de combate se mide en **fotogramas de juego**, no en segundos. A 60 fps un
fotograma son 16,67 ms. Las tres fases de un ataque:

| Fase | Definición | Qué significa para ti |
|---|---|---|
| **Arranque** (*startup*) | «El tiempo que ocurre tras pulsar el botón de ataque pero antes de que el ataque pueda hacer contacto» | Los fotogramas de anticipación. Es lo que hace el ataque **esquivable** |
| **Activo** (*active*) | «El tiempo en que un movimiento tiene *hitbox* y puede hacer daño» | Cuando existe `obj_hitbox`. Suele ser **1‑4 fotogramas** aunque el ataque entero dure 30 |
| **Recuperación** (*recovery*) | «El tiempo posterior a que el ataque deje de golpear, pero antes de recuperar el control» | El castigo por fallar. Sin esto, el jugador hace *spam* del botón |

> ⚠️ **Trampa de convención.** La comunidad de juegos de lucha **cuenta el primer fotograma
> activo dentro del arranque**. Dustloop lo define así: *«Startup: el tiempo antes de que un
> ataque esté activo, incluyendo el primer fotograma activo. Un ataque con 10F de arranque no
> hace nada durante 9 fotogramas y golpea en el décimo.»* Infil lo confirma: *«las comunidades
> de muchos juegos cuentan por partida doble el primer fotograma activo»*.
> **En este documento `arranque` NO incluye el primer activo** (es más fácil de programar). Un
> ataque de `arranque: 4, activo: 3` empieza a golpear en el fotograma 5 y en la notación de
> Dustloop sería «arranque 5F». Si publicas frame data, tradúcela.

El resto del vocabulario, en una tabla, para que el equipo hable el mismo idioma:

| Término | Qué es |
|---|---|
| **Hitstun** | «El tiempo en que tu personaje no puede hacer nada tras ser golpeado». Si vuelves a golpear antes de que acabe, **eso es un combo** |
| **Blockstun** | Lo mismo pero al bloquear. Es más corto que el hitstun: por eso bloquear te devuelve el turno antes |
| **Ventaja en frames** (*frame advantage*) | «Quién se recupera primero cuando un golpe entra o se bloquea». Si te recuperas antes que él, estás «a favor» (*plus*); si no, «en contra» (*minus*) |
| **Cancel** | «Eliminar la recuperación de un ataque, normalmente para encadenar otro». Es la base de los combos desde hace décadas |
| **Hit confirm** | «Ejecutar un ataque, ver que ha entrado, y sólo entonces continuar la cadena». Si lo bloquean, te paras |
| **I-frames** (invulnerabilidad) | «Un estado en el que es imposible golpearte». Suele implementarse **quitando las hurtboxes** |
| **Prioridad** | Un sistema en el que ciertos ataques siempre ganan a otros si se cruzan. No todos los juegos lo tienen: en Street Fighter 6 los ataques de cualquier fuerza pueden empatar (*trade*) |
| **Armadura / poise** | «Un estado en el que un personaje absorbe un golpe sin entrar en hitstun», y puede seguir atacando. También «super armor» |
| **Juggle** | Golpear a un rival **en el aire** desde el suelo. Los ataques que hacen malabares lo lanzan alto y lo mantienen cerca |
| **Escalado de daño** | «Un sistema que reduce el daño de cada golpe del combo cada vez más según el combo se alarga». Sin él, los combos largos se descontrolan |
| **Contragolpe** (*counter hit*) | Golpear a alguien **durante el arranque** de su ataque. Suele hacer más daño y dar más ventaja |
| **Input buffer** | La ventana de tiempo en la que el juego acepta y guarda una pulsación. Ya resuelto en [`scr_input_buffer.gml`](../06%20-%20Assets%20y%20Scripts/scr_input_buffer.gml) |

**Referencias hechas en GameMaker:** *Katana ZERO* (un golpe mata, i-frames de parry),
*Hyper Light Drifter* (dash con i-frames, cadena de tres tajos), *Nuclear Throne* (multi-hit y
knockback), *Pizza Tower* (combate por embestida). El curso en español que monta un beat 'em up
completo es el de **Hektor Profe**
([10 · 01, curso 7](../10%20-%20Cursos%20en%20español/01%20-%20Academia%20de%20Hektor%20Profe.md)) —
5 lecciones, centrado en la máquina de estados de animación; su curso 6, el Action RPG de 13
lecciones, tiene el estado de ataque y las colisiones con enemigos, y es más útil para esto.

### 1.3 Subgéneros: qué cambia

| Subgénero | Arranque típico | Cajas | Lo que de verdad lo define |
|---|---|---|---|
| Beat 'em up (*Streets of Rage*) | 6‑10 F | Hitbox grande, generosa | Golpear a varios a la vez, profundidad en Y, agarres |
| Hack and slash (*Devil May Cry*) | 4‑8 F | Hitbox larga, multi-hit | *Cancels* muy permisivos: la expresión del jugador |
| Action RPG (*Zelda*, *Hyper Light*) | 8‑14 F | Hitbox en arco | Stats, resistencias, gestión de la stamina |
| Plataformas con espada (*Hollow Knight*) | 3‑6 F | Hitbox que empuja al jugador (*pogo*) | El ataque es también movilidad |
| Lucha (*Street Fighter*) | 3‑20 F | Muchas cajas por fotograma | Frame data exacta, ventaja, prioridad, escalado |

---

## 2. Arquitectura recomendada

### 2.1 Jerarquía de objetos

```
obj_entidad            (padre: vida, hurtbox, hitstun, i-frames, aguante — sin sprite)
├── obj_jugador        (input + combos + parry + esquiva)
└── obj_enemigo        (padre de enemigos: IA de combate)
    ├── obj_enemigo_melee
    └── obj_enemigo_a_distancia

obj_hitbox             (instancia EFÍMERA: sólo datos, ninguna lógica propia)
obj_combate            (controlador persistente: resuelve TODAS las cajas y la cola)
```

**Por qué `obj_hitbox` no tiene lógica propia.** El manual de eventos es tajante
([01 · 06 §4](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md)): puedes
confiar en el orden de los **eventos**, pero **no** en el orden de las instancias dentro de un
evento. Si cada hitbox se recolocara y detectara por su cuenta, unas mirarían al dueño ya
movido y otras al dueño de hace un fotograma, **según el orden de creación**. Ese es el bug de
«la hitbox va un fotograma por detrás» y es intermitente, que es lo peor que puede ser un bug.

La solución es un **único controlador** que hace todo el trabajo de combate en su `End Step`,
cuando todas las entidades ya se han movido:

```
┌─ Step ────────────────────────────────────────────────────┐
│  Las entidades leen input, deciden y SE MUEVEN            │
└───────────────────────────────────────────────────────────┘
┌─ End Step  (obj_combate, y sólo él) ──────────────────────┐
│  1. Recolocar cada obj_hitbox sobre su dueño              │
│  2. Detectar solapes hitbox ↔ hurtbox → ENCOLAR           │
│  3. Resolver empates y prioridad                          │
│  4. Aplicar la cola: recibir_golpe() una vez por golpe    │
│  5. Envejecer y destruir las hitboxes caducadas           │
└───────────────────────────────────────────────────────────┘
```

### 2.2 Las dos arquitecturas posibles (y cuál elegir)

Hay exactamente dos formas de montar esto. Las dos son válidas; **la primera es la que
recomiendo** para el 90 % de los juegos.

| | **A · Instancia efímera** (recomendada) | **B · Tabla de datos pura** |
|---|---|---|
| Qué es la hitbox | Una instancia de `obj_hitbox` que vive N fotogramas | Un rectángulo calculado y comprobado cada fotograma activo, sin instancias |
| Estado propio | Sí: lista de golpeados, edad, dueño, prioridad | Hay que guardarlo en el atacante |
| Puede sobrevivir al ataque | **Sí** (una onda expansiva, un tajo que se queda) | No |
| Puede moverse sola | **Sí** (una hitbox que avanza: embestidas, proyectiles cuerpo a cuerpo) | No |
| Se ve en el depurador | **Sí**, es una instancia | No |
| Coste | Una instancia por golpe (usa *pooling*) | Cero instancias |
| Varias cajas por fotograma | Una instancia por caja | Trivial: un array de rectángulos |
| Ideal para | Beat 'em up, hack and slash, ARPG, plataformas | Juego de lucha con frame data exacta y decenas de cajas |

La B se resuelve en cuatro líneas y aparece en la §5.11: es literalmente
`collision_rectangle_list()` sobre el rectángulo del ataque, cada fotograma activo. La versión
mínima de esa comprobación ya está escrita en
[13 · 04 §3.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md);
aquí lo que crece es la **tabla**.

### 2.3 Los datos: un struct por ataque

El ataque es **dato**, no código. Esto no es purismo: es lo que permite tener un arma con más
alcance sin duplicar una sola línea de lógica, y lo que permite cargar los ataques desde JSON
([01 · 14](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md)).

| Struct | Responsabilidad |
|---|---|
| `global.ataques` | Frame data + caja + daño + reglas de *cancel*, por ataque |
| `global.armas` | Multiplicadores de alcance y daño. Un arma **no** redefine los ataques |
| `EstadoCombate` | Vida, aguante, hitstun, i-frames, contador de combo — vive en la entidad |
| `global.cola_golpes` | Los golpes detectados este fotograma, sin aplicar todavía |

---

## 3. El bucle central (core loop)

Orden exacto de un fotograma de combate. Cada número está en un evento concreto **a propósito**.

```
┌─ Begin Step  (obj_jugador) ───────────────────────────────┐
│  1. Leer input y meterlo en el buffer (scr_input_buffer)  │
└───────────────────────────────────────────────────────────┘
┌─ Step  (todas las entidades) ─────────────────────────────┐
│  2. Tick del estado de combate: hitstun--, iframes--,     │
│     aguante se recarga, el combo se olvida                │
│  3. Si hitstun > 0 → sólo inercia, NO se lee input        │
│  4. FSM: ¿empieza un ataque? ¿se puede cancelar?          │
│  5. ataque_frame++ y, si toca, crear la hitbox            │
│  6. Movimiento y move_and_collide()                       │
└───────────────────────────────────────────────────────────┘
┌─ End Step  (obj_combate, único) ──────────────────────────┐
│  7. Recolocar todas las hitboxes sobre sus dueños         │
│  8. Detectar solapes → encolar golpes                     │
│  9. Resolver prioridad y empates                          │
│ 10. Aplicar la cola → recibir_golpe()                     │
│ 11. Envejecer y destruir hitboxes                         │
└───────────────────────────────────────────────────────────┘
┌─ End Step  (obj_camara) ──────────────────────────────────┐
│ 12. La cámara sigue al jugador YA movido (04 · 01 §5.7)   │
└───────────────────────────────────────────────────────────┘
┌─ Draw / Draw GUI ─────────────────────────────────────────┐
│ 13. draw_self(), parpadeo de i-frames                     │
│ 14. Depuración: cajas rojas y verdes (sólo si procede)    │
└───────────────────────────────────────────────────────────┘
```

> **El daño NUNCA se aplica en un evento Draw.** Es el error de la §7 que más cuesta
> diagnosticar: el `Draw` no se ejecuta si la instancia está fuera de la vista, si el juego
> pausa el dibujado o si `visible = false`. Un enemigo fuera de cámara se volvería inmortal.

---

## 4. Sistemas clave

### 4.1 La hurtbox como dato

Un rectángulo relativo al origen, con **X positiva hacia delante**. Al voltear el personaje
(`image_xscale = -1`) el rectángulo se refleja solo. Cada estado puede tener la suya: agacharse
la encoge, esquivar la borra, un ataque puede **estirarla** (la contrapartida honesta de tener
más alcance).

```
        origen (x, y)
             │
   ┌─────────┼─────────┐
   │         │         │   dx = desplazamiento hacia delante
   │      ┌──┼──┐      │   dy = desplazamiento hacia arriba (negativo)
   │      │ HURT│      │   ancho, alto
   │      └──┼──┘      │
   └─────────┼─────────┘
```

### 4.2 Multi-hit y la lista de ya golpeados

Un ataque con 3 fotogramas activos hace daño **tres veces** si no lo impides. La lista de ya
golpeados es la que convierte «3 fotogramas activos» en «un golpe».

Para ataques que **sí** deben golpear varias veces (un molinete, una llama continua) no se
borra la lista: se guarda **en qué fotograma** golpeó a cada uno y se le vuelve a permitir
golpear pasados `refresco` fotogramas. Es exactamente el `set_rehurt_timing()` de la librería
*HitBoxes_gml* de MichelV, que define ese parámetro como «el tiempo transcurrido necesario
(en steps) para que la hitbox hiera dos veces a la misma entidad».

### 4.3 Hitstun, blockstun y ventaja

```
Ataque:   [arranque 5][activo 3][recuperación 10]
                       │
                       └─ el golpe entra en el fotograma 6

Atacante:  ...................|recuperación 10|  → libre en el fotograma 18
Víctima:                      |hitstun 14     |  → libre en el fotograma 22
                                              ↑
                                     ventaja = +4 para el atacante
```

La cuenta es `ventaja = hitstun_o_blockstun - fotogramas_de_recuperacion_restantes`. Si es
positiva, el atacante actúa antes: puede encadenar. Si es negativa, el defensor puede
castigarle. **La regla de diseño:** un ataque debe ser positivo al golpear y ligeramente
negativo al ser bloqueado. Si es positivo al bloquear, el jugador puede repetirlo eternamente.

### 4.4 Cancels y combos por cadena de estados

Un combo no es una lista de ataques: es una **ventana de tiempo** dentro de la recuperación en
la que se acepta el siguiente ataque de la cadena.

```
ligero_1:  [arranque 4][activo 3][recuperación 9]
                                 ├──ventana de cancel──┤
                                 5                    12
           Si pulsas ataque entre los fotogramas 5 y 12 → ligero_2
           Si no pulsas → recuperación completa y vuelta a "quieto"
```

Con `cancela_en_vacio: false` la ventana **sólo se abre si el golpe conectó**: eso es el
*hit confirm*, y evita que el jugador se lance a una cadena larga contra un enemigo que la
está bloqueando.

### 4.5 I-frames y esquiva

Los i-frames se implementan **quitando la hurtbox**, no ignorando el daño. Es la misma cosa
para el motor y una cosa distinta para el diseño: si quitas la caja, un ataque que «debía»
darte simplemente pasa a través, y las cajas de depuración lo enseñan.

Una esquiva típica: `arranque 2` (vulnerable), `i-frames 10`, `recuperación 8` (vulnerable).
Los 2 fotogramas iniciales sin invulnerabilidad son lo que hace que la esquiva **tenga
timing** en vez de ser un botón de «no me pasa nada».

### 4.6 Bloqueo y parry

| Mecánica | Ventana | Efecto | Riesgo |
|---|---|---|---|
| **Bloqueo** | Mientras mantengas | Daño 0 o reducido, blockstun, empuje | Ninguno, pero pierdes el turno |
| **Parry** | 4‑8 fotogramas desde la pulsación | Anula el golpe **y** deja al atacante indefenso | Si fallas, quedas expuesto |

Infil describe el parry como «un mecanismo que te permite apartar un golpe entrante y
[recuperarte] casi al instante. Normalmente un parry con éxito concede una oportunidad enorme
de contraataque». El bloqueo, en cambio, «hace contacto con tu cuerpo, pero no recibes daño».
Al bloquear entras en blockstun.

Nota importante para un juego con orientación libre: **el bloqueo debe ser direccional**. Si
bloqueas golpes que vienen por la espalda, el bloqueo deja de ser una decisión.

### 4.7 Aguante (*poise* / super armor)

El aguante es lo que evita que un enemigo grande sea *stun-lockeado* hasta la muerte. Cada
golpe le resta `rompe_aguante`; mientras le quede aguante **recibe daño pero no hitstun ni
empuje** — sigue atacando. Cuando llega a cero, se tambalea (`hitstun` completo) y el aguante
se recarga tras unos fotogramas.

Es el «super armor» de Infil: «un estado en el que un personaje puede absorber un golpe sin
entrar en hitstun, lo que le permite seguir atacando o moviéndose». Y su contrapartida
canónica: «a veces los ataques multi-golpe muy rápidos consiguen atravesarlo».

### 4.8 Empuje, juggle y escalado de daño

- **Empuje** (*knockback*): implementado en
  [04 · 15 §5.4](./15%20-%20Game%20feel%20y%20juice.md) (`apply_knockback`). No lo repitas.
- **Juggle**: si la víctima está en el aire, el golpe le añade elevación. Para que el combo
  **termine**, cada golpe del mismo combo eleva menos: `elevacion * power(0.75, juggles)`.
  Es el equivalente al *hit stun deterioration* que documenta Infil: «el personaje golpeado
  sufre cada vez menos hitstun según el combo se alarga».
- **Escalado de daño**: una tabla de multiplicadores por número de golpe. Sin ella, cualquier
  combo que descubra un jugador creativo rompe el juego.

### 4.9 Selección de objetivo en cono

En un juego con orientación libre, el ataque no debe salir «hacia donde apunta el sprite» sino
**hacia el enemigo válido más cercano dentro de un cono**. Se resuelve con `point_direction()`,
`angle_difference()` y `point_distance()`: tres funciones, y el combate deja de sentirse
resbaladizo.

### 4.10 Armas con alcance distinto

Un arma **no** define ataques nuevos: define **multiplicadores** sobre los mismos. Una lanza es
`alcance: 1.6, dano: 0.9`; unos puños son `alcance: 0.6, dano: 0.7, arranque: 0.8` (más
rápidos). Cambiar de arma es cambiar un struct.

---

## 5. Código base

### 5.0 Configuración (`scr_combate_config`)

```gml
// ---------------------------------------------------------------------------
// scr_combate_config — constantes del sistema de combate.
// ---------------------------------------------------------------------------

// Equipos: dos entidades del mismo equipo no se golpean entre sí.
#macro EQUIPO_JUGADOR   0
#macro EQUIPO_ENEMIGO   1
#macro EQUIPO_NEUTRO    2   // trampas y explosiones: golpean a todo el mundo

// Ventanas de sensación (en fotogramas, a 60 fps)
#macro COMBO_OLVIDO_FRAMES   45   // sin recibir golpes, el contador de combo se resetea
#macro AGUANTE_RECARGA       90   // fotogramas sin ser golpeado para recuperar el aguante
#macro PARRY_VENTANA          6   // fotogramas de gracia del parry
#macro IFRAMES_TRAS_GOLPE    30   // invulnerabilidad tras recibir daño (0 = sin gracia)
#macro CARGA_FRAMES          24   // fotogramas manteniendo el botón para el ataque cargado

// Búsqueda de víctimas: margen alrededor de la hitbox para la fase amplia.
#macro CAJA_MARGEN_BUSQUEDA  48

// Depuración de cajas. Ponlo a false antes de publicar.
#macro DEPURAR_CAJAS         true

// Escalado de daño por número de golpe del combo (índice 0 = primer golpe).
#macro ESCALADO_COMBO  [1.00, 1.00, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10]

// La cola de golpes detectados este fotograma, sin resolver todavía.
global.cola_golpes = [];
```

### 5.1 La tabla de ataques (los datos)

```gml
// ---------------------------------------------------------------------------
// scr_ataques — frame data. Se ejecuta una vez al arrancar el juego.
//
// CONVENCIÓN DE FOTOGRAMAS (importante):
//   arranque     = fotogramas ANTES del primer activo (no lo incluye).
//   activo       = fotogramas en los que existe la hitbox.
//   recuperacion = fotogramas hasta recuperar el control.
//   El primer fotograma activo es el (arranque + 1). En la notación de
//   Dustloop este mismo ataque se anunciaría como "arranque (arranque + 1) F".
//
// LA CAJA es relativa al origen, con X POSITIVA HACIA DELANTE e Y POSITIVA
// HACIA ABAJO (como en GameMaker). Se voltea sola con image_xscale.
// Campos opcionales: rompe_bloqueo (bool), rebote (real).
// ---------------------------------------------------------------------------
global.ataques =
{
    // --- Cadena ligera: rápida, encadenable, poco daño ----------------------
    ligero_1 : {
        sprite : spr_jugador_ligero_1,
        arranque : 4, activo : 3, recuperacion : 9,
        caja : { dx : 16, dy : -10, ancho : 22, alto : 18 },
        dano : 6, empuje : 3.0, elevacion : 0,
        hitstun : 14, blockstun : 8, rompe_aguante : 1, prioridad : 1,
        refresco : 0,                          // 0 = un golpe por víctima
        cancela_a : ["ligero_2"], cancel_ini : 5, cancel_fin : 12,
        cancela_en_vacio : false,              // hit confirm: sólo si conectó
        sonido : snd_espada_ligero
    },
    ligero_2 : {
        sprite : spr_jugador_ligero_2,
        arranque : 3, activo : 3, recuperacion : 11,
        caja : { dx : 18, dy : -10, ancho : 24, alto : 18 },
        dano : 7, empuje : 3.5, elevacion : 0,
        hitstun : 15, blockstun : 8, rompe_aguante : 1, prioridad : 1,
        refresco : 0,
        cancela_a : ["pesado"], cancel_ini : 5, cancel_fin : 14,
        cancela_en_vacio : false,
        sonido : snd_espada_ligero
    },

    // --- Remate de la cadena: lento, lanza al aire (permite juggle) ---------
    pesado : {
        sprite : spr_jugador_pesado,
        arranque : 11, activo : 4, recuperacion : 20,
        caja : { dx : 22, dy : -12, ancho : 30, alto : 24 },
        dano : 18, empuje : 7.0, elevacion : -5,
        hitstun : 26, blockstun : 12, rompe_aguante : 3,
        prioridad : 2,                         // gana a los ligeros si se cruzan
        refresco : 0,
        cancela_a : [], cancel_ini : 0, cancel_fin : 0,   // último de la cadena
        cancela_en_vacio : false,
        sonido : snd_espada_pesado
    },

    // --- Cargado: se lanza al SOLTAR el botón. Atraviesa bloqueo y armadura -
    cargado : {
        sprite : spr_jugador_cargado,
        arranque : 18, activo : 5, recuperacion : 24,
        caja : { dx : 26, dy : -12, ancho : 38, alto : 26 },
        dano : 30, empuje : 9.0, elevacion : -7,
        hitstun : 34, blockstun : 20, rompe_aguante : 99, prioridad : 3,
        refresco : 0,
        cancela_a : [], cancel_ini : 0, cancel_fin : 0,
        cancela_en_vacio : false, rompe_bloqueo : true,
        sonido : snd_espada_cargado
    },

    // --- Aéreo hacia abajo: el "pogo" de los plataformas -------------------
    aereo_abajo : {
        sprite : spr_jugador_aereo,
        arranque : 5, activo : 6, recuperacion : 6,
        caja : { dx : 0, dy : 14, ancho : 24, alto : 20 },
        dano : 8, empuje : 2.0, elevacion : 0,
        hitstun : 12, blockstun : 6, rompe_aguante : 1, prioridad : 1,
        refresco : 0,
        cancela_a : [], cancel_ini : 0, cancel_fin : 0,
        cancela_en_vacio : false,
        rebote : -8,                           // al conectar, impulsa al atacante
        sonido : snd_espada_ligero
    },

    // --- Molinete: MULTI-HIT, golpea a la misma víctima cada 6 fotogramas ---
    molinete : {
        sprite : spr_jugador_molinete,
        arranque : 8, activo : 30, recuperacion : 16,
        caja : { dx : 0, dy : -10, ancho : 46, alto : 22 },
        dano : 3, empuje : 1.0, elevacion : -1,
        hitstun : 8, blockstun : 4, rompe_aguante : 1, prioridad : 1,
        refresco : 6,
        cancela_a : [], cancel_ini : 0, cancel_fin : 0,
        cancela_en_vacio : false,
        sonido : snd_espada_ligero
    }
};

// ---------------------------------------------------------------------------
// Armas: MULTIPLICADORES sobre los mismos ataques. No redefinen frame data.
// Cambiar de arma es cambiar un struct: ni una línea de lógica se toca.
// ---------------------------------------------------------------------------
global.armas =
{
    espada : { alcance : 1.00, dano : 1.00, arranque : 1.00 },
    lanza  : { alcance : 1.60, dano : 0.90, arranque : 1.20 },  // largo y lento
    daga   : { alcance : 0.70, dano : 0.65, arranque : 0.70 },  // corto y rápido
    punos  : { alcance : 0.55, dano : 0.50, arranque : 0.60 }
};
```

### 5.2 Las fases del ataque

```gml
// ---------------------------------------------------------------------------
// scr_ataques_fases
// ---------------------------------------------------------------------------
enum FaseAtaque { ARRANQUE, ACTIVO, RECUPERACION, FUERA }

/// @func fase_del_ataque(_def, _frame)
/// @desc En qué fase está un ataque en un fotograma dado.
/// @param {Struct} _def     Entrada de global.ataques.
/// @param {Real}   _frame   Fotograma del ataque, empezando en 1.
/// @returns {Real}          Un miembro de FaseAtaque.
function fase_del_ataque(_def, _frame)
{
    var _f = floor(_frame);
    if (_f < 1) return FaseAtaque.FUERA;

    if (_f <= _def.arranque) return FaseAtaque.ARRANQUE;

    if (_f <= _def.arranque + _def.activo) return FaseAtaque.ACTIVO;

    if (_f <= _def.arranque + _def.activo + _def.recuperacion)
    {
        return FaseAtaque.RECUPERACION;
    }

    return FaseAtaque.FUERA;
}

/// @func duracion_del_ataque(_def)
/// @desc Fotogramas totales del ataque, de la primera anticipación al control.
/// @param {Struct} _def
/// @returns {Real}
function duracion_del_ataque(_def)
{
    return _def.arranque + _def.activo + _def.recuperacion;
}

/// @func primer_frame_activo(_def)
/// @desc El fotograma en el que aparece la hitbox. Aquí es donde se crea.
/// @param {Struct} _def
/// @returns {Real}
function primer_frame_activo(_def)
{
    return _def.arranque + 1;
}
```

> **Sobre leer `image_index` en vez de llevar un contador.** Es tentador y lo hace todo el
> mundo, pero `image_index` es un **real**, avanza a `image_speed` y se ve afectado por el
> hit stop. Si quieres frame data exacta, **manda el contador y obedece el sprite**:
>
> ```gml
> // En el enter del estado de ataque:
> ataque_frame = 0;
> sprite_index = _def.sprite;
> image_index  = 0;
> // Que la animación dure EXACTAMENTE los fotogramas de la tabla:
> image_speed  = image_number / duracion_del_ataque(_def);
> ```
>
> Si prefieres que mande el artista (el sprite decide cuándo golpea), usa
> `fase_del_ataque(_def, floor(image_index) + 1)` y acepta que el frame data depende de
> `image_speed`. Las dos opciones son legítimas; mezclarlas no.

### 5.3 `obj_hitbox` — Create (sólo datos)

```gml
// ---------------------------------------------------------------------------
// obj_hitbox — Create
// Instancia EFÍMERA. No tiene Step, ni Draw de juego, ni colisiones propias:
// todo lo resuelve obj_combate en su End Step. Ver §2.1.
// Sprite: ninguno.  visible = false.
// ---------------------------------------------------------------------------
visible = false;

// --- Identidad -------------------------------------------------------------
dueno    = noone;        // instancia que la creó
equipo   = EQUIPO_NEUTRO;
def      = undefined;    // struct de global.ataques (para el sonido y el debug)

// --- Geometría, en el espacio del dueño (X hacia delante) -------------------
off_x = 0;
off_y = 0;
ancho = 16;
alto  = 16;

// --- Efecto ----------------------------------------------------------------
dano          = 1;
empuje        = 3;
elevacion     = 0;
hitstun       = 12;
blockstun     = 8;
rompe_aguante = 1;
rompe_bloqueo = false;
prioridad     = 1;
rebote        = 0;       // impulso vertical que devuelve al atacante (pogo)

// --- Vida y repetición -----------------------------------------------------
frames_vida  = 3;
refresco     = 0;        // 0 = un golpe por víctima; >0 = multi-hit cada N frames
edad         = 0;
sigue_al_dueno = true;
vel_propia_x = 0;        // si no sigue al dueño, puede avanzar sola
vel_propia_y = 0;

// --- Contabilidad ----------------------------------------------------------
// Array de structs { objetivo, frame }. NO se limpia nunca durante la vida de
// la caja: cuando la caja muere, muere la lista con ella. Si reutilizas la
// instancia con un pool, VACÍALA A MANO (ver §7).
ya_golpeados = [];

// Posición absoluta de la caja, recalculada por obj_combate cada fotograma.
caja_x1 = x;  caja_y1 = y;  caja_x2 = x;  caja_y2 = y;
```

### 5.4 Crear la hitbox desde el ataque

```gml
// ---------------------------------------------------------------------------
// scr_combate_cajas
// ---------------------------------------------------------------------------

/// @func golpe_desde_definicion(_def, _arma)
/// @desc Traduce un ataque + un arma a los campos de EFECTO que lee
///       recibir_golpe(). Lo usan las dos arquitecturas de la §2.2: en la A
///       estos campos se copian a la instancia, en la B se pasan tal cual.
/// @param {Struct} _def   Entrada de global.ataques.
/// @param {Struct} _arma  Entrada de global.armas (multiplicadores).
/// @returns {Struct}
function golpe_desde_definicion(_def, _arma)
{
    return {
        dano          : _def.dano * _arma.dano,
        empuje        : _def.empuje,
        elevacion     : _def.elevacion,
        hitstun       : _def.hitstun,
        blockstun     : _def.blockstun,
        rompe_aguante : _def.rompe_aguante,
        prioridad     : _def.prioridad,
        rompe_bloqueo : variable_struct_exists(_def, "rompe_bloqueo") ? _def.rompe_bloqueo : false,
        rebote        : variable_struct_exists(_def, "rebote")        ? _def.rebote        : 0
    };
}

/// @func caja_de_golpe_crear(_def, _arma)
/// @desc Crea la hitbox de un ataque sobre la instancia que llama.
///       Llámala UNA sola vez, en el primer fotograma activo del ataque.
/// @param {Struct} _def   Entrada de global.ataques.
/// @param {Struct} _arma  Entrada de global.armas.
/// @returns {Id.Instance} La hitbox creada.
function caja_de_golpe_crear(_def, _arma)
{
    var _alc = _arma.alcance;
    var _e   = golpe_desde_definicion(_def, _arma);

    return instance_create_layer(x, y, layer, obj_hitbox,
    {
        dueno : id, equipo : equipo, def : _def,

        // La caja se escala y se desplaza con el alcance del arma.
        off_x : _def.caja.dx * _alc,       off_y : _def.caja.dy,
        ancho : _def.caja.ancho * _alc,    alto  : _def.caja.alto,

        dano          : _e.dano,          empuje        : _e.empuje,
        elevacion     : _e.elevacion,     hitstun       : _e.hitstun,
        blockstun     : _e.blockstun,     rompe_aguante : _e.rompe_aguante,
        prioridad     : _e.prioridad,     rompe_bloqueo : _e.rompe_bloqueo,
        rebote        : _e.rebote,

        frames_vida : _def.activo,        refresco : _def.refresco
    });
}

/// @func caja_en_mundo(_inst)
/// @desc Convierte la caja relativa de una hitbox a coordenadas del mundo,
///       volteándola según el image_xscale de su dueño.
///       Escribe caja_x1/y1/x2/y2 en la propia hitbox.
/// @param {Id.Instance} _inst  La hitbox.
/// @returns {Bool}  false si el dueño ya no existe.
function caja_en_mundo(_inst)
{
    with (_inst)
    {
        if (!instance_exists(dueno)) return false;

        // El signo del dueño es lo que voltea la caja. Sin esto, el personaje
        // golpea siempre hacia la derecha: es EL bug clásico (§7).
        var _signo = sign(dueno.image_xscale);
        if (_signo == 0) _signo = 1;

        var _cx = dueno.x + off_x * _signo;
        var _cy = dueno.y + off_y;

        x = _cx;
        y = _cy;

        caja_x1 = _cx - ancho * 0.5;
        caja_y1 = _cy - alto  * 0.5;
        caja_x2 = _cx + ancho * 0.5;
        caja_y2 = _cy + alto  * 0.5;
    }

    return true;
}
```

### 5.5 La hurtbox y el estado de combate

```gml
// ---------------------------------------------------------------------------
// obj_entidad — Create (padre de jugador y enemigos)
// ---------------------------------------------------------------------------
equipo = EQUIPO_NEUTRO;

// La máscara de MOVIMIENTO. Fija, rectangular, a los pies. No cambia jamás.
mask_index = spr_mascara_movimiento;

// La HURTBOX, en el espacio local (X hacia delante, Y hacia abajo).
// Es un struct para poder cambiarla por estado sin tocar la máscara.
hurtbox = { dx : 0, dy : -14, ancho : 14, alto : 28 };

// Estado de combate (ver §6)
combate = new EstadoCombate(3, 8);   // 3 de aguante, 8 de vida

vel_x = 0;
vel_y = 0;
```

```gml
// ---------------------------------------------------------------------------
// scr_combate_hurtbox
// ---------------------------------------------------------------------------

/// @func zona_vulnerable(_inst)
/// @desc Rectángulo de la hurtbox de una instancia, en coordenadas del mundo.
///       Devuelve undefined si la instancia es invulnerable AHORA MISMO: eso
///       es lo que implementa los i-frames (no hay caja, no hay golpe).
/// @param {Id.Instance} _inst
/// @returns {Struct|Undefined}  { x1, y1, x2, y2 }
function zona_vulnerable(_inst)
{
    if (!instance_exists(_inst)) return undefined;

    with (_inst)
    {
        if (!variable_instance_exists(id, "hurtbox")) return undefined;
        if (!variable_instance_exists(id, "combate")) return undefined;
        if (combate.iframes > 0)  return undefined;   // esquiva, gracia tras golpe
        if (combate.vida <= 0)    return undefined;   // ya está muerto

        var _signo = sign(image_xscale);
        if (_signo == 0) _signo = 1;

        var _cx = x + hurtbox.dx * _signo;
        var _cy = y + hurtbox.dy;

        return {
            x1 : _cx - hurtbox.ancho * 0.5,
            y1 : _cy - hurtbox.alto  * 0.5,
            x2 : _cx + hurtbox.ancho * 0.5,
            y2 : _cy + hurtbox.alto  * 0.5
        };
    }
}

/// @func hurtbox_cambiar(_dx, _dy, _ancho, _alto)
/// @desc Reemplaza la hurtbox de la instancia que llama. Úsala en el `enter`
///       de un estado: agacharse la encoge, un ataque largo la estira.
function hurtbox_cambiar(_dx, _dy, _ancho, _alto)
{
    hurtbox = { dx : _dx, dy : _dy, ancho : _ancho, alto : _alto };
}
```

### 5.6 El controlador: detectar, encolar, resolver

```gml
// ---------------------------------------------------------------------------
// obj_combate — Create   (persistente, uno por partida, sin sprite)
// ---------------------------------------------------------------------------
persistent = true;
visible    = true;        // sólo para dibujar las cajas de depuración
global.cola_golpes = [];
```

```gml
// ---------------------------------------------------------------------------
// obj_combate — End Step
// TODO el combate se resuelve aquí, y sólo aquí. Ver §2.1 para el porqué.
// ---------------------------------------------------------------------------

// === 1. Recolocar cada hitbox sobre su dueño ================================
with (obj_hitbox)
{
    if (sigue_al_dueno)
    {
        // Si el dueño ha muerto durante este fotograma, la caja se va con él.
        if (!caja_en_mundo(id)) { instance_destroy(); continue; }
    }
    else
    {
        // Caja independiente: avanza sola (embestidas, ondas expansivas).
        x += vel_propia_x;
        y += vel_propia_y;
        caja_x1 = x - ancho * 0.5;  caja_y1 = y - alto * 0.5;
        caja_x2 = x + ancho * 0.5;  caja_y2 = y + alto * 0.5;
    }
}

// === 2. Detectar solapes y encolar =========================================
global.cola_golpes = [];

with (obj_hitbox)
{
    var _caja = id;

    // --- Fase amplia: candidatos cerca de la caja ---------------------------
    // Iteramos las entidades y descartamos por distancia. No usamos una DS list
    // porque la hurtbox NO coincide con la máscara de movimiento: una fase
    // amplia basada en máscaras se perdería los brazos estirados.
    var _radio = (max(ancho, alto) * 0.5) + CAJA_MARGEN_BUSQUEDA;

    with (obj_entidad)
    {
        // Mismo equipo (y el neutro golpea a todos): fuera.
        if (equipo == _caja.equipo && _caja.equipo != EQUIPO_NEUTRO) continue;

        // No golpearse a uno mismo.
        if (id == _caja.dueno) continue;

        // Descarte barato por distancia antes de calcular nada.
        if (point_distance(x, y, _caja.x, _caja.y) > _radio) continue;

        // --- Fase estrecha: rectángulo contra rectángulo --------------------
        var _zona = zona_vulnerable(id);
        if (is_undefined(_zona)) continue;    // invulnerable o muerto

        if (!rectangle_in_rectangle(_caja.caja_x1, _caja.caja_y1,
                                    _caja.caja_x2, _caja.caja_y2,
                                    _zona.x1, _zona.y1, _zona.x2, _zona.y2))
        {
            continue;
        }

        // --- ¿Ya la golpeamos? ----------------------------------------------
        if (!caja_puede_golpear(_caja, id)) continue;

        // --- Encolar. NO se aplica daño aquí. --------------------------------
        // La dirección sale del dueño; si ya no existe (caja independiente que
        // le sobrevive), sale de la propia caja.
        var _ox = instance_exists(_caja.dueno) ? _caja.dueno.x : _caja.x;
        var _oy = instance_exists(_caja.dueno) ? _caja.dueno.y : _caja.y;
        var _dir = point_direction(_ox, _oy, x, y);

        array_push(global.cola_golpes, {
            caja      : _caja,
            atacante  : _caja.dueno,
            victima   : id,
            direccion : _dir,
            prioridad : _caja.prioridad
        });
    }
}

// === 3. Resolver prioridad y empates =======================================
cola_golpes_priorizar();

// === 4. Aplicar la cola ====================================================
var _n = array_length(global.cola_golpes);
for (var i = 0; i < _n; i++)
{
    var _g = global.cola_golpes[i];

    if (!instance_exists(_g.victima))  continue;
    if (!instance_exists(_g.caja))     continue;

    // Apuntar el golpe en la caja ANTES de aplicarlo: si la víctima muere y
    // se destruye, la caja ya no podría anotarlo.
    array_push(_g.caja.ya_golpeados, { objetivo : _g.victima, frame : _g.caja.edad });

    // Avisar al atacante de que el golpe conectó: es el "hit confirm" que
    // abre la ventana de cancel (§5.8).
    if (instance_exists(_g.atacante))
    {
        _g.atacante.golpe_confirmado = true;

        // Rebote del ataque aéreo hacia abajo (pogo).
        if (_g.caja.rebote != 0) _g.atacante.vel_y = _g.caja.rebote;
    }

    with (_g.victima) recibir_golpe(_g);
}
global.cola_golpes = [];

// === 5. Envejecer y destruir ===============================================
with (obj_hitbox)
{
    edad++;
    if (edad >= frames_vida) instance_destroy();
}
```

```gml
// ---------------------------------------------------------------------------
// scr_combate_cola
// ---------------------------------------------------------------------------

/// @func caja_puede_golpear(_caja, _victima)
/// @desc ¿Puede esta hitbox golpear a esta víctima ahora?
///       refresco == 0  → una sola vez en toda su vida.
///       refresco  > 0  → cada `refresco` fotogramas (multi-hit).
/// @param {Id.Instance} _caja
/// @param {Id.Instance} _victima
/// @returns {Bool}
function caja_puede_golpear(_caja, _victima)
{
    var _lista = _caja.ya_golpeados;
    var _n = array_length(_lista);

    for (var i = 0; i < _n; i++)
    {
        if (_lista[i].objetivo != _victima) continue;

        // Ya está en la lista.
        if (_caja.refresco <= 0) return false;                     // un solo golpe
        return (_caja.edad - _lista[i].frame) >= _caja.refresco;   // multi-hit
    }

    return true;   // nunca golpeada
}

/// @func cola_golpes_priorizar()
/// @desc Resuelve los cruces: si A golpea a B y B golpea a A en el mismo
///       fotograma, gana el de más prioridad y el otro golpe se descarta.
///       Con prioridades iguales, los dos entran (es un "trade").
///       Si tu juego no tiene sistema de prioridad, borra la llamada: los
///       empates son legítimos y así funcionan Street Fighter IV y 6.
function cola_golpes_priorizar()
{
    var _n = array_length(global.cola_golpes);
    if (_n < 2) return;

    var _sobreviven = [];

    for (var i = 0; i < _n; i++)
    {
        var _a = global.cola_golpes[i];
        var _descartado = false;

        for (var j = 0; j < _n; j++)
        {
            if (i == j) continue;
            var _b = global.cola_golpes[j];

            // ¿Es el golpe recíproco? (B golpea justo al atacante de A)
            var _reciproco = (_b.victima == _a.atacante)
                          && (_b.atacante == _a.victima);

            if (_reciproco && _b.prioridad > _a.prioridad)
            {
                _descartado = true;
                break;
            }
        }

        if (!_descartado) array_push(_sobreviven, _a);
    }

    global.cola_golpes = _sobreviven;
}
```

### 5.7 `recibir_golpe()` — el receptor

```gml
// ---------------------------------------------------------------------------
// scr_combate_recibir
// ---------------------------------------------------------------------------

/// @func recibir_golpe(_golpe)
/// @desc Aplica un golpe a la instancia que llama. Se ejecuta DENTRO de un
///       `with (victima)`, así que `combate`, `vel_x` y `vel_y` son suyos.
///
///       Esta función se ocupa de las REGLAS (bloqueo, parry, aguante, daño,
///       escalado, juggle). Toda la SENSACIÓN —hit stop, sacudida, partículas,
///       flash, número flotante— la delega en hit_complete(), que está en
///       04 · 15 §5.7. No la reimplementes aquí.
///
/// @param {Struct} _golpe  { caja, atacante, victima, direccion }
/// @returns {Bool}  true si el golpe hizo daño.
function recibir_golpe(_golpe)
{
    var _caja = _golpe.caja;
    var _dir  = _golpe.direccion;

    // --- 1. Parry: la ventana más corta y la recompensa más grande ----------
    if (combate.parry > 0 && bloqueo_valido(_dir))
    {
        combate.parry = 0;
        combate.blockstun = 0;

        // El atacante queda indefenso: se le corta el ataque y se le mete una
        // recuperación larga. Ahí está la ventana de castigo.
        if (instance_exists(_golpe.atacante))
        {
            with (_golpe.atacante)
            {
                combate.hitstun = max(combate.hitstun, 30);
                fsm.set("aturdido");
            }
        }

        audio_play_sound(snd_parry, 10, false);
        hit_stop(6);                          // 04 · 15 §5.0
        return false;
    }

    // --- 2. Bloqueo --------------------------------------------------------
    if (combate.bloqueando && bloqueo_valido(_dir) && !_caja.rompe_bloqueo)
    {
        combate.blockstun = max(combate.blockstun, _caja.blockstun);
        combate.vida     -= floor(_caja.dano * 0.15);   // chip damage, opcional

        // El bloqueo empuja, pero mucho menos.
        vel_x += lengthdir_x(_caja.empuje * 0.35, _dir);

        audio_play_sound(snd_bloqueo, 10, false);
        return false;
    }

    // --- 3. Aguante / super armor -------------------------------------------
    combate.aguante        -= _caja.rompe_aguante;
    combate.aguante_espera  = AGUANTE_RECARGA;
    var _rompe = (combate.aguante <= 0);

    // --- 4. Contragolpe: golpear durante el arranque del rival --------------
    var _contra = variable_instance_exists(id, "ataque_frame")
               && (ataque_frame > 0)
               && (fase_del_ataque(ataque_def, ataque_frame) == FaseAtaque.ARRANQUE);

    // --- 5. Daño, con escalado de combo -------------------------------------
    var _mult = escalado_de_dano(combate.combo_golpes) * (_contra ? 1.25 : 1.0);
    var _dano = max(1, round(_caja.dano * _mult));

    combate.vida         -= _dano;
    combate.combo_golpes += 1;
    combate.combo_olvido  = COMBO_OLVIDO_FRAMES;

    // --- 6. Hitstun y empuje: SÓLO si se rompió el aguante -------------------
    if (_rompe)
    {
        combate.hitstun = max(combate.hitstun, _caja.hitstun + (_contra ? 6 : 0));
        combate.aguante = 0;

        // Empuje: implementación en 04 · 15 §5.4.
        apply_knockback(id, _dir, _caja.empuje, combate.hitstun);

        // Juggle: cada golpe del mismo combo eleva menos, para que el combo
        // termine. Es el "hit stun deterioration" de los juegos de lucha.
        if (_caja.elevacion != 0)
        {
            vel_y = _caja.elevacion * power(0.75, combate.juggles);
            combate.juggles += 1;
        }
    }

    // --- 7. Invulnerabilidad de gracia --------------------------------------
    // En un beat 'em up el jugador la necesita; los enemigos casi nunca (si no,
    // no se pueden hacer combos contra ellos). De ahí que sea por entidad.
    if (combate.iframes_de_gracia > 0)
    {
        combate.iframes = combate.iframes_de_gracia;
    }

    // --- 8. Toda la sensación, de una vez (04 · 15 §5.7) ---------------------
    hit_complete(id, _dano, _dir);

    return true;
}

/// @func bloqueo_valido(_dir)
/// @desc ¿Viene el golpe por delante? Un bloqueo que para golpes por la espalda
///       deja de ser una decisión. 90° a cada lado del frente.
/// @param {Real} _dir  Dirección del golpe: del atacante hacia la víctima.
/// @returns {Bool}
function bloqueo_valido(_dir)
{
    var _signo  = sign(image_xscale);
    if (_signo == 0) _signo = 1;
    var _frente = (_signo > 0) ? 0 : 180;

    // _dir apunta HACIA nosotros, así que el golpe viene de la dirección opuesta.
    var _origen = _dir + 180;

    return abs(angle_difference(_origen, _frente)) <= 90;
}

/// @func escalado_de_dano(_golpes_previos)
/// @desc Multiplicador de daño según cuántos golpes lleva ya el combo.
/// @param {Real} _golpes_previos
/// @returns {Real}  Entre 0.10 y 1.00.
function escalado_de_dano(_golpes_previos)
{
    var _tabla = ESCALADO_COMBO;
    var _i = clamp(floor(_golpes_previos), 0, array_length(_tabla) - 1);
    return _tabla[_i];
}
```

### 5.8 El jugador: combos, cancels y buffer

```gml
// ---------------------------------------------------------------------------
// obj_jugador — Create (fragmento de combate; hereda de obj_entidad)
// ---------------------------------------------------------------------------
event_inherited();

equipo = EQUIPO_JUGADOR;
combate.iframes_de_gracia = IFRAMES_TRAS_GOLPE;

arma_actual = global.armas.espada;

// --- Ataque en curso -------------------------------------------------------
ataque_nombre    = "";
ataque_def       = undefined;
ataque_frame     = 0;
caja_creada      = false;
golpe_confirmado = false;     // lo pone obj_combate al conectar (hit confirm)
ya_golpeados     = [];        // sólo para la arquitectura B (§5.11)

// --- Buffer de entrada: la pulsación no se pierde ---------------------------
// Implementación completa en 06 · scr_input_buffer.gml
buffer_ligero = new InputBuffer(8);
buffer_pesado = new InputBuffer(8);
buffer_esquiva = new InputBuffer(6);

// --- Carga del ataque pesado -----------------------------------------------
carga_frames  = 0;   // fotogramas que lleva pulsado el botón
carga_soltada = 0;   // los que llevaba en el momento de soltarlo

fsm = fsm_bind(id, estados_del_jugador(), "quieto");   // 06 · scr_state_machine.gml
```

```gml
// ---------------------------------------------------------------------------
// obj_jugador — Begin Step: leer el input, y nada más.
// ---------------------------------------------------------------------------
var _ligero  = keyboard_check_pressed(ord("J")) || gamepad_button_check_pressed(0, gp_face3);
var _esquiva = keyboard_check_pressed(vk_shift) || gamepad_button_check_pressed(0, gp_face2);

// El pesado sale al SOLTAR, no al pulsar: es lo que permite cargarlo con el
// mismo botón. Si saliera al pulsar, la carga nunca llegaría a acumularse.
var _pesado_hold    = keyboard_check(ord("K"))          || gamepad_button_check(0, gp_face4);
var _pesado_soltado = keyboard_check_released(ord("K")) || gamepad_button_check_released(0, gp_face4);

if (_pesado_hold)    carga_frames++;
if (_pesado_soltado) { carga_soltada = carga_frames; carga_frames = 0; }

buffer_ligero.update(_ligero);
buffer_pesado.update(_pesado_soltado);
buffer_esquiva.update(_esquiva);
```

```gml
// ---------------------------------------------------------------------------
// scr_jugador_estados — los estados de combate
// ---------------------------------------------------------------------------

/// @func estados_del_jugador()
/// @desc Struct de estados para fsm_bind(). Sólo la parte de combate; los
///       estados de movimiento (quieto/correr/salto) van en 04 · 01 §5.5.
/// @returns {Struct}
function estados_del_jugador()
{
    return
    {
        quieto :
        {
            update : function()
            {
                if (combate.hitstun > 0) { fsm.set("aturdido"); exit; }

                if (buffer_esquiva.consume()) { fsm.set("esquiva"); exit; }

                // Al soltar el botón pesado: cargado si llegó al umbral,
                // pesado normal si no. Un solo botón, dos ataques.
                if (buffer_pesado.consume())
                {
                    ataque_empezar(carga_soltada >= CARGA_FRAMES ? "cargado" : "pesado");
                    carga_soltada = 0;
                    exit;
                }

                if (buffer_ligero.consume()) { ataque_empezar("ligero_1"); exit; }
            }
        },

        atacando :
        {
            enter : function()
            {
                ataque_frame     = 0;
                caja_creada      = false;
                golpe_confirmado = false;
                ya_golpeados     = [];        // sólo lo usa la arquitectura B

                sprite_index = ataque_def.sprite;
                image_index  = 0;
                // La animación dura EXACTAMENTE lo que dice la tabla.
                image_speed  = image_number / duracion_del_ataque(ataque_def);

                // Atacar te EXPONE: la hurtbox crece hacia delante. Es la
                // contrapartida honesta de tener alcance (§4.1).
                hurtbox_cambiar(4, -14, 18, 28);

                vel_x *= 0.3;   // el ataque frena: el peso se siente
            },

            update : function()
            {
                if (combate.hitstun > 0) { fsm.set("aturdido"); exit; }

                ataque_frame++;

                var _fase = fase_del_ataque(ataque_def, ataque_frame);

                // 1) Crear la hitbox en el PRIMER fotograma activo, una vez.
                if (!caja_creada && ataque_frame >= primer_frame_activo(ataque_def))
                {
                    caja_de_golpe_crear(ataque_def, arma_actual);
                    caja_creada = true;
                    audio_play_sound(ataque_def.sonido, 10, false);
                }

                // 2) Ventana de cancel: encadenar el siguiente de la cadena.
                if (ataque_cancelable(ataque_def, ataque_frame, golpe_confirmado)
                &&  buffer_ligero.disponible()
                &&  array_length(ataque_def.cancela_a) > 0)
                {
                    buffer_ligero.consume();
                    ataque_empezar(ataque_def.cancela_a[0]);
                    exit;
                }

                // Cancelar a esquiva es lo que hace que el combate no se sienta
                // "pegajoso". Coste: hay que gastar algo (stamina, recurso).
                if (_fase == FaseAtaque.RECUPERACION && buffer_esquiva.consume())
                {
                    fsm.set("esquiva");
                    exit;
                }

                // 3) Fin del ataque.
                if (_fase == FaseAtaque.FUERA) fsm.set("quieto");
            },

            exit : function()
            {
                image_speed  = 1;
                ataque_frame = 0;
                hurtbox_cambiar(0, -14, 14, 28);   // vuelta a la caja neutra
            }
        },

        esquiva :
        {
            enter : function()
            {
                sprite_index = spr_jugador_esquiva;
                image_index  = 0;

                var _signo = sign(image_xscale);
                if (_signo == 0) _signo = 1;
                vel_x = _signo * 7;

                // 2 fotogramas vulnerables ANTES de los i-frames: eso es lo que
                // hace que la esquiva tenga timing en vez de ser un "no me das".
                combate.iframes = 0;
                combate.esquiva_frame = 0;
            },

            update : function()
            {
                combate.esquiva_frame++;

                if (combate.esquiva_frame == 3) combate.iframes = 10;

                vel_x = lerp(vel_x, 0, 0.18);

                if (combate.esquiva_frame >= 20) fsm.set("quieto");
            }
        },

        bloqueando :
        {
            enter  : function() { combate.bloqueando = true;  sprite_index = spr_jugador_bloqueo; },
            exit   : function() { combate.bloqueando = false; combate.parry = 0; },
            update : function()
            {
                if (combate.blockstun > 0) exit;   // atado al bloqueo
                if (!keyboard_check(ord("L"))) fsm.set("quieto");
            }
        },

        aturdido :
        {
            enter  : function() { sprite_index = spr_jugador_dano; image_index = 0; },
            update : function()
            {
                // Durante el hitstun NO se lee input: sólo inercia.
                if (combate.hitstun <= 0) fsm.set("quieto");
            }
        }
    };
}

/// @func ataque_empezar(_nombre)
/// @desc Arranca un ataque de la tabla. Es el único sitio donde se asigna
///       ataque_def: si aparece en otro, hay dos fuentes de verdad.
/// @param {String} _nombre  Clave de global.ataques.
function ataque_empezar(_nombre)
{
    if (!variable_struct_exists(global.ataques, _nombre))
    {
        show_debug_message("ataque_empezar: no existe el ataque \"" + _nombre + "\"");
        return;
    }

    ataque_nombre = _nombre;
    ataque_def    = global.ataques[$ _nombre];
    fsm.set("atacando");
}

/// @func ataque_cancelable(_def, _frame, _confirmado)
/// @desc ¿Estamos dentro de la ventana de cancel? Con cancela_en_vacio = false
///       la ventana sólo se abre si el golpe conectó: eso es el HIT CONFIRM.
/// @param {Struct} _def
/// @param {Real}   _frame
/// @param {Bool}   _confirmado  ¿Ha conectado ya este ataque?
/// @returns {Bool}
function ataque_cancelable(_def, _frame, _confirmado)
{
    if (_def.cancel_fin <= 0) return false;
    if (_frame < _def.cancel_ini || _frame > _def.cancel_fin) return false;
    if (!_def.cancela_en_vacio && !_confirmado) return false;
    return true;
}
```

### 5.9 El parry, en cuatro líneas

```gml
// ---------------------------------------------------------------------------
// obj_jugador — Step (fragmento, ANTES de fsm.update())
// ---------------------------------------------------------------------------
// El parry es una ventana corta que se abre al PULSAR bloqueo, no al mantenerlo.
if (keyboard_check_pressed(ord("L")) && !fsm.is("atacando"))
{
    combate.parry = PARRY_VENTANA;
    fsm.set("bloqueando");
}
```

`combate.parry` se decrementa en `EstadoCombate.tick()` (§6). Todo lo demás lo hace
`recibir_golpe()`: si llega un golpe mientras `parry > 0`, gana el defensor.

### 5.10 Dibujar las cajas (depuración)

```gml
// ---------------------------------------------------------------------------
// obj_combate — Draw End
// Se dibuja DESPUÉS de todo lo demás para que las cajas queden encima.
// Colores según la convención de la comunidad de juegos de lucha:
//   ROJO   = hitbox   (lo que golpea)
//   VERDE  = hurtbox  (lo que puede ser golpeado)
//   AZUL   = máscara de movimiento
//   AMARILLO = entidad invulnerable (i-frames): no tiene hurtbox ahora mismo
// ---------------------------------------------------------------------------
if (!DEPURAR_CAJAS && !is_debug_overlay_open()) exit;

var _color_previo = draw_get_color();
var _alpha_previo = draw_get_alpha();

// --- Máscaras de movimiento (azul) ------------------------------------------
draw_set_color(c_blue);
draw_set_alpha(0.35);
with (obj_entidad)
{
    draw_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom, true);
}

// --- Hurtboxes (verde) ------------------------------------------------------
with (obj_entidad)
{
    var _z = zona_vulnerable(id);

    if (is_undefined(_z))
    {
        // Sin caja: invulnerable. Se marca en amarillo sobre la máscara para
        // que se VEA que los i-frames están activos (§7: el error de no verlos).
        draw_set_color(c_yellow);
        draw_set_alpha(0.30);
        draw_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom, false);
    }
    else
    {
        draw_set_color(c_lime);
        draw_set_alpha(0.60);
        draw_rectangle(_z.x1, _z.y1, _z.x2, _z.y2, true);
    }
}

// --- Hitboxes (rojo) --------------------------------------------------------
draw_set_color(c_red);
draw_set_alpha(0.55);
with (obj_hitbox)
{
    draw_rectangle(caja_x1, caja_y1, caja_x2, caja_y2, false);
}

draw_set_color(_color_previo);
draw_set_alpha(_alpha_previo);
```

```gml
// ---------------------------------------------------------------------------
// obj_combate — Draw GUI  (el frame data en vivo: vale por mil pruebas)
// ---------------------------------------------------------------------------
if (!DEPURAR_CAJAS) exit;
if (!instance_exists(obj_jugador)) exit;

draw_set_color(c_white);

with (obj_jugador)
{
    var _txt = "estado: " + fsm.get()
             + "\nataque: " + string(ataque_nombre) + "  f" + string(ataque_frame);

    if (ataque_def != undefined)
    {
        var _fase = fase_del_ataque(ataque_def, ataque_frame);
        var _nombres = ["ARRANQUE", "ACTIVO", "RECUPERACION", "-"];
        _txt += "  [" + _nombres[_fase] + "]";
    }

    _txt += "\nvida: "    + string(combate.vida)    + "/" + string(combate.vida_max)
         +  "  aguante: " + string(combate.aguante) + "/" + string(combate.aguante_max)
         +  "\nhitstun: " + string(combate.hitstun)
         +  "  iframes: " + string(combate.iframes)
         +  "  combo: "   + string(combate.combo_golpes);

    draw_text(8, 8, _txt);
}

draw_text(8, 88, "hitboxes vivas: " + string(instance_number(obj_hitbox)));
```

### 5.11 La arquitectura B: sin instancias

Si tu juego es de lucha y necesitas frame data exacta con muchas cajas, no crees instancias:
comprueba el rectángulo directamente cada fotograma activo. Es la variante que ya insinúa
[13 · 04 §3.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md),
escrita entera:

```gml
// ---------------------------------------------------------------------------
// obj_jugador — Step, dentro del estado "atacando" (arquitectura B)
// No hay obj_hitbox: el rectángulo se comprueba y se olvida.
// Requiere `ya_golpeados = [];` en el Create y vaciarlo en el `enter` del
// estado de ataque — la lista vive en el ATACANTE, no en la caja.
// ---------------------------------------------------------------------------
if (fase_del_ataque(ataque_def, ataque_frame) == FaseAtaque.ACTIVO)
{
    var _signo = sign(image_xscale);
    if (_signo == 0) _signo = 1;

    var _alc = arma_actual.alcance;
    var _cx  = x + ataque_def.caja.dx * _alc * _signo;
    var _cy  = y + ataque_def.caja.dy;
    var _hw  = ataque_def.caja.ancho * _alc * 0.5;
    var _hh  = ataque_def.caja.alto * 0.5;

    // El EFECTO del golpe es el mismo struct plano de la §5.4. recibir_golpe()
    // sólo LEE campos de `caja`, así que le da igual que sea una instancia
    // (arquitectura A) o un struct suelto (esta).
    var _efecto = golpe_desde_definicion(ataque_def, arma_actual);

    // collision_rectangle_list devuelve el NÚMERO de instancias y llena la lista.
    // Ojo: usa la MÁSCARA de las víctimas, no su hurtbox. Vale si en tu juego
    // hurtbox == máscara; si no, quédate con la arquitectura A.
    var _lista = ds_list_create();
    var _num = collision_rectangle_list(_cx - _hw, _cy - _hh, _cx + _hw, _cy + _hh,
                                        obj_enemigo, false, true, _lista, true);

    for (var i = 0; i < _num; i++)
    {
        var _v = _lista[| i];

        if (array_contains(ya_golpeados, _v)) continue;
        array_push(ya_golpeados, _v);

        var _dir = point_direction(x, y, _v.x, _v.y);
        var _golpe = { caja : _efecto, atacante : id, victima : _v, direccion : _dir };

        with (_v) recibir_golpe(_golpe);
    }

    ds_list_destroy(_lista);   // SIEMPRE. Las DS list no se recogen solas.
}
```

> ⚠️ `ds_list_destroy()` es obligatorio: las estructuras DS **no** las libera el recolector de
> basura. Una `ds_list_create()` por fotograma sin destruir es una fuga de memoria que crece
> hasta que el juego se cae. Es el motivo por el que la arquitectura A, que no crea listas,
> es más difícil de estropear. Si necesitas la lista de instancias en la posición exacta de una
> instancia (no de un rectángulo), la función hermana es `instance_place_list(x, y, obj, list,
> ordered)`, con la misma obligación de destruir.

### 5.12 El enemigo mínimo: patrulla → telegrafía → ataque → recuperación

```gml
// ---------------------------------------------------------------------------
// obj_enemigo_melee — Create   (hereda de obj_entidad)
// ---------------------------------------------------------------------------
event_inherited();

equipo = EQUIPO_ENEMIGO;
combate = new EstadoCombate(2, 12);
combate.iframes_de_gracia = 0;   // los enemigos NO tienen gracia: si no, no hay combos

arma_actual   = global.armas.punos;
ataque_nombre = "";
ataque_def    = undefined;
ataque_frame  = 0;
caja_creada   = false;

objetivo      = noone;
patrulla_dir  = 1;
descanso      = 0;

// Ataque propio del enemigo, con arranque MUY largo: esa es la telegrafía.
global.ataques.enemigo_zarpazo =
{
    sprite        : spr_enemigo_zarpazo,
    arranque      : 26,      // ~0,43 s de aviso: el jugador puede reaccionar
    activo        : 4,
    recuperacion  : 34,      // la ventana de castigo
    caja          : { dx : 18, dy : -10, ancho : 26, alto : 20 },
    dano          : 10, empuje : 4.5, elevacion : 0,
    hitstun       : 20, blockstun : 10,
    rompe_aguante : 1, prioridad : 1, refresco : 0,
    cancela_a     : [], cancel_ini : 0, cancel_fin : 0,
    cancela_en_vacio : false,
    sonido        : snd_zarpazo
};

fsm = fsm_bind(id, {
    patrulla :
    {
        update : function()
        {
            vel_x = patrulla_dir * 1.2;
            image_xscale = patrulla_dir;

            // Girar en el borde de la plataforma o contra la pared.
            if (place_meeting(x + patrulla_dir * 4, y, obj_solido)
            || !place_meeting(x + patrulla_dir * 10, y + 2, obj_solido))
            {
                patrulla_dir *= -1;
            }

            var _obj = objetivo_en_cono(120, 70, obj_jugador);
            if (_obj != noone) { objetivo = _obj; fsm.set("acercarse"); }
        }
    },

    acercarse :
    {
        update : function()
        {
            if (!instance_exists(objetivo)) { fsm.set("patrulla"); exit; }

            var _signo = sign(objetivo.x - x);
            if (_signo != 0) image_xscale = _signo;
            vel_x = _signo * 2.0;

            // El alcance de ataque sale de la TABLA, no de un número suelto.
            var _def = global.ataques.enemigo_zarpazo;
            var _alcance = (_def.caja.dx + _def.caja.ancho * 0.5) * arma_actual.alcance;

            if (abs(objetivo.x - x) < _alcance && descanso <= 0)
            {
                ataque_nombre = "enemigo_zarpazo";
                ataque_def    = _def;
                fsm.set("atacando");
            }

            descanso--;
        }
    },

    atacando :
    {
        enter : function()
        {
            ataque_frame = 0;
            caja_creada  = false;
            vel_x        = 0;
            sprite_index = ataque_def.sprite;
            image_index  = 0;
            image_speed  = image_number / duracion_del_ataque(ataque_def);
        },

        update : function()
        {
            if (combate.hitstun > 0) { fsm.set("aturdido"); exit; }

            ataque_frame++;
            var _fase = fase_del_ataque(ataque_def, ataque_frame);

            // LA TELEGRAFÍA. Sin esto el ataque es injusto: no se puede leer.
            if (_fase == FaseAtaque.ARRANQUE)
            {
                var _t = ataque_frame / ataque_def.arranque;
                image_blend = merge_color(c_white, c_red, _t);
            }
            else
            {
                image_blend = c_white;
            }

            if (!caja_creada && ataque_frame >= primer_frame_activo(ataque_def))
            {
                caja_de_golpe_crear(ataque_def, arma_actual);
                caja_creada = true;
                audio_play_sound(ataque_def.sonido, 10, false);
            }

            if (_fase == FaseAtaque.FUERA)
            {
                descanso = 40;         // no encadena ataques: da turno al jugador
                fsm.set("acercarse");
            }
        },

        exit : function() { image_blend = c_white; image_speed = 1; }
    },

    aturdido :
    {
        enter  : function() { sprite_index = spr_enemigo_dano; image_index = 0; },
        update : function() { if (combate.hitstun <= 0) fsm.set("acercarse"); }
    }
}, "patrulla");
```

```gml
// ---------------------------------------------------------------------------
// scr_combate_objetivo
// ---------------------------------------------------------------------------

/// @func objetivo_en_cono(_alcance, _semiangulo, _objeto)
/// @desc La instancia más cercana de _objeto dentro de un cono delante de
///       quien llama. Con esto el ataque va hacia el enemigo, no hacia donde
///       resulte que mira el sprite.
/// @param {Real} _alcance     Radio máximo en píxeles.
/// @param {Real} _semiangulo  Grados a cada lado del frente (70 es generoso).
/// @param {Asset.GMObject} _objeto
/// @returns {Id.Instance}     noone si no hay nadie.
function objetivo_en_cono(_alcance, _semiangulo, _objeto)
{
    var _signo = sign(image_xscale);
    if (_signo == 0) _signo = 1;
    var _frente = (_signo > 0) ? 0 : 180;

    var _mejor = noone;
    var _mejor_dist = _alcance + 1;
    var _ox = x;
    var _oy = y;

    with (_objeto)
    {
        if (id == other.id) continue;
        if (variable_instance_exists(id, "combate") && combate.vida <= 0) continue;

        var _d = point_distance(_ox, _oy, x, y);
        if (_d > _alcance || _d >= _mejor_dist) continue;

        var _a = point_direction(_ox, _oy, x, y);
        if (abs(angle_difference(_a, _frente)) > _semiangulo) continue;

        _mejor = id;
        _mejor_dist = _d;
    }

    return _mejor;
}
```

### 5.13 El registro de daño

Depurar a ojo cuánto daño hace cada cosa deja de escalar en cuanto hay tipos, resistencias y
escudos de por medio (`combate.vida -= _dano` ya no cuenta toda la historia). El desglose por
fuente, el DPS medido y el panel de Debug Overlay que lo enseñan en partida están en
[04 · 32 §5.13](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#513-el-registro-de-daño-medir-lo-que-de-verdad-pasa),
sobre `telemetria_registrar()` de
[13 · 01 §9.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md).

---

## 6. Gestión del estado de combate

Todo lo que un golpe puede modificar vive en **un struct**, no en variables sueltas del objeto.
Razón práctica: `tick()` es una sola llamada, se ve entero en el depurador, y se serializa a
JSON sin tocar la instancia.

```gml
// ---------------------------------------------------------------------------
// scr_estado_combate
// ---------------------------------------------------------------------------

/// @func EstadoCombate(_aguante_max, _vida_max)
/// @desc Estado de combate de una entidad. Uno por instancia.
/// @param {Real} _aguante_max  Golpes que aguanta sin tambalearse (super armor).
/// @param {Real} _vida_max
function EstadoCombate(_aguante_max, _vida_max) constructor
{
    // --- Vitales -----------------------------------------------------------
    vida     = _vida_max;
    vida_max = _vida_max;

    // --- Aturdimientos -----------------------------------------------------
    hitstun   = 0;    // sin control tras recibir un golpe
    blockstun = 0;    // sin control tras bloquear

    // --- Defensas ----------------------------------------------------------
    iframes           = 0;    // >0 → zona_vulnerable() devuelve undefined
    iframes_de_gracia = 0;    // los que se conceden tras un golpe (0 = ninguno)
    bloqueando        = false;
    parry             = 0;    // ventana de parry restante
    esquiva_frame     = 0;

    // --- Aguante (poise / super armor) --------------------------------------
    aguante        = _aguante_max;
    aguante_max    = _aguante_max;
    aguante_espera = 0;       // fotogramas sin recibir golpes para recargar

    // --- Combo recibido ------------------------------------------------------
    combo_golpes = 0;         // golpes seguidos: alimenta el escalado de daño
    combo_olvido = 0;         // fotogramas para olvidar el combo
    juggles      = 0;         // veces elevado en este combo

    /// @desc Un tick por fotograma. Llámalo AL PRINCIPIO del Step de la entidad.
    static tick = function()
    {
        if (hitstun   > 0) hitstun--;
        if (blockstun > 0) blockstun--;
        if (iframes   > 0) iframes--;
        if (parry     > 0) parry--;

        // El combo se olvida si pasan COMBO_OLVIDO_FRAMES sin recibir golpes.
        if (combo_olvido > 0)
        {
            combo_olvido--;
            if (combo_olvido == 0) { combo_golpes = 0; juggles = 0; }
        }

        // El aguante se recarga entero, no poco a poco: así el jugador aprende
        // cuándo el enemigo vuelve a tener armadura.
        if (aguante_espera > 0)
        {
            aguante_espera--;
            if (aguante_espera == 0) aguante = aguante_max;
        }
    };

    /// @desc ¿Puede la entidad actuar por su cuenta este fotograma?
    /// @returns {Bool}
    static tiene_control = function()
    {
        return (hitstun <= 0) && (blockstun <= 0) && (vida > 0);
    };

    /// @desc Cura sin pasarse del máximo.
    static curar = function(_cantidad)
    {
        vida = min(vida + _cantidad, vida_max);
    };

    /// @desc Struct plano listo para json_stringify(). Los aturdimientos NO se
    ///       guardan: al cargar una partida nadie debe estar en hitstun.
    static serializar = function()
    {
        return { vida : vida, vida_max : vida_max,
                 aguante_max : aguante_max };
    };
}
```

Y en el `Step` de `obj_entidad`, **lo primero de todo**:

```gml
// ---------------------------------------------------------------------------
// obj_entidad — Step
// ---------------------------------------------------------------------------
combate.tick();

// Durante el hitstun sólo hay inercia: no se lee input, no se ataca.
if (!combate.tiene_control())
{
    vel_x = lerp(vel_x, 0, 0.18);
    exit;                                  // los hijos ya no ejecutan su lógica
}

// Parpadeo de i-frames: si no se ve, el jugador cree que el juego se comió el golpe.
image_alpha = (combate.iframes > 0 && (combate.iframes div 3) % 2 == 0) ? 0.35 : 1;

// Muerte
if (combate.vida <= 0 && !fsm.is("muerto")) fsm.set("muerto");
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Un solo rectángulo para todo | El personaje es más fácil de golpear en ciertos fotogramas; la colisión con paredes cambia al atacar | Tres cajas: `mask_index` fija, `hurtbox` en datos, `obj_hitbox` aparte (§1.1) |
| **Golpear dos veces por fotograma** | Un ataque con 3 activos hace el triple de daño | Lista `ya_golpeados` en la **hitbox**, consultada con `caja_puede_golpear()` (§5.6) |
| **La hitbox va un fotograma por detrás** | El golpe entra "tarde"; a veces sí y a veces no | Ningún `Step` en `obj_hitbox`: todo se recoloca en el `End Step` de `obj_combate` (§2.1) |
| **Las cajas no se voltean** | El personaje sólo golpea hacia la derecha | Multiplicar `off_x` y `hurtbox.dx` por `sign(image_xscale)` (§5.4, §5.5) |
| **Daño en un evento `Draw`** | Los enemigos fuera de cámara son inmortales; al pausar el dibujado el combate se congela | El daño se aplica en `End Step`. El `Draw` sólo dibuja (§3) |
| **No vaciar `ya_golpeados` al reutilizar la caja** | Con *pooling*, la segunda vez que sale el ataque no golpea a nadie | Al sacar una instancia del pool: `ya_golpeados = []; edad = 0;`. Ver [`scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml) |
| **I-frames invisibles** | El jugador cree que el juego se comió su golpe | Parpadeo con `image_alpha` (§6) y amarillo en las cajas de depuración (§5.10) |
| **Ataques sin recuperación** | *Spam* del botón: el combate no tiene ritmo ni riesgo | `recuperacion` ≥ 8 fotogramas en el más rápido; el pesado, ≥ 20 |
| **Enemigos sin telegrafía** | El jugador sólo puede reaccionar por reflejos, o memorizando | `arranque` ≥ 20 fotogramas en los enemigos + señal visual (`image_blend`) durante toda la fase (§5.12) |
| Escalar el sprite con `image_xscale` para el squash | Las cajas cambian de tamaño al animar | El squash va en el `Draw` con `draw_sprite_ext()` ([04 · 15 §5.3](./15%20-%20Game%20feel%20y%20juice.md)) |
| `ds_list_create()` sin `ds_list_destroy()` | La memoria crece hasta que el juego se cae | Destruir siempre, en el mismo bloque (§5.11) |
| Hitstun sin cortar el input | El enemigo sigue atacando mientras sale volando: el empuje no se lee como castigo | `if (!combate.tiene_control()) exit;` al principio del Step (§6) |
| Aguante que se recarga poco a poco | El jugador no sabe nunca si el enemigo tiene armadura | Recarga **entera** tras `AGUANTE_RECARGA` fotogramas sin recibir golpes (§6) |
| Combos sin escalado de daño | Un jugador descubre un bucle y el jefe muere en dos segundos | Tabla `ESCALADO_COMBO` + `juggles` decrecientes (§4.8) |
| Bloqueo omnidireccional | Bloquear deja de ser una decisión | `bloqueo_valido()`: 90° a cada lado del frente (§5.7) |
| Mezclar `image_index` y contador de fotogramas | El frame data cambia si tocas `image_speed` o si hay hit stop | Elige uno. Si mandas tú: `image_speed = image_number / total` (§5.2) |
| Crear la hitbox en el `enter` del estado | El golpe sale en el fotograma 1: no hay arranque, no es esquivable | Crearla cuando `ataque_frame >= primer_frame_activo()` (§5.8) |

---

## 8. Cómo escalarlo

Orden recomendado. Cada paso es jugable antes de pasar al siguiente.

1. **Un ataque, una hitbox, un enemigo que muere.** Con `DEPURAR_CAJAS = true` desde el primer
   minuto: sin ver las cajas estás programando a ciegas.
2. **Frame data real**: arranque, activo y recuperación distintos de cero. Aquí es donde el
   combate empieza a sentirse.
3. **Hitstun + empuje** (delegando en [04 · 15 §5.4](./15%20-%20Game%20feel%20y%20juice.md)) y
   **hit stop**. Dos fotogramas de congelación cambian el juego entero.
4. **La cadena de tres**: `ligero_1 → ligero_2 → pesado` con ventanas de cancel y hit confirm.
5. **Esquiva con i-frames.** Es la mecánica que más aumenta la sensación de control.
6. **Aguante en los enemigos grandes** y telegrafía larga en todos.
7. **Escalado de daño y juggle** cuando los combos empiecen a ser largos.
8. **Bloqueo y parry**, si el juego premia la defensa activa.
9. **Object pooling de las hitboxes** ([`scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml))
   cuando haya más de ~30 cajas simultáneas. Antes, no: es optimización prematura.

**Cuando el sistema crezca:**

- **Editor de cajas.** Cuando la tabla pase de 15 ataques, escribir números a mano deja de
  funcionar. Dos caminos: (a) una *room* de edición donde colocas rectángulos con el ratón y
  vuelcas el resultado a JSON; (b) capas de datos en Aseprite —un rectángulo rojo y uno verde
  en capas aparte— y un script que las lea al exportar. La opción (a) no necesita herramientas
  externas y es la que recomiendo empezar.
- **Ataques en JSON.** `global.ataques` es un struct plano a propósito: `json_stringify()` /
  `json_parse()` funcionan directamente. Diseñadores editando frame data sin recompilar es la
  diferencia entre iterar diez veces al día y dos.
  Ver [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md).
- **Multi-caja por ataque.** Cambiar `caja : {...}` por `cajas : [ {...}, {...} ]` y crear una
  hitbox por entrada. El resto del sistema no se entera.
- **Cajas por fotograma.** Un array `por_frame : [ undefined, undefined, {caja}, {caja} ]` para
  ataques cuya caja se mueve durante los activos (un tajo en arco).
- **Sincronización en red.** El combate determinista que aquí queda montado —input → estado →
  cola de golpes— es exactamente lo que necesita el *rollback*: puedes rebobinar y re-simular
  porque nada depende del orden de las instancias. Ver
  [04 · 14 §4.6 — Rollback completo](./14%20-%20Multijugador.md).
- **Agarres.** Son un ataque más con una caja propia y `rompe_bloqueo: true`, más un estado
  compartido entre las dos entidades. Es el primer sistema que rompe la independencia entre
  atacante y víctima: déjalo para el final.

---

## Ver también

- [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — hit stop, sacudida de
  cámara, empuje, partículas, flash y `hit_complete()`. **Todo el feedback vive ahí.**
- [13 · 04 — Animación de sprites, Sequences y Animation Curves](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md) —
  origen del sprite, `mask_index` fija, broadcast messages y la tabla mínima de frame data.
- [04 · 23 — IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) —
  cómo se acerca el enemigo antes de atacar.
- [04 · 01 — Plataformas 2D](./01%20-%20Plataformas%202D.md) — movimiento, cámara y la FSM base.
- [04 · 02 — Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) — orden por Y y
  combate a distancia.
- [04 · 04 — RPG / Action RPG](./04%20-%20RPG%20_%20Action%20RPG.md) — stats de ataque y defensa, inventario
  y progresión, y la decisión «por turnos frente a acción».
- [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  **resistencias por tipo de daño**, armadura, escudos y el motor de **efectos de estado**
  (veneno, quemadura, congelación, aturdimiento, ralentización) que faltaban aquí: engancha
  directamente en `recibir_golpe()` (§5.7 de este documento).
- [04 · 14 — Multijugador](./14%20-%20Multijugador.md) — rollback y determinismo.
- [01 · 08 — Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) —
  máscaras, bounding boxes y las funciones `collision_*`.
- [01 · 06 — Eventos y ciclo del juego](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) —
  por qué `End Step` es el único sitio fiable.
- [06 · `scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) ·
  [`scr_input_buffer.gml`](../06%20-%20Assets%20y%20Scripts/scr_input_buffer.gml) ·
  [`scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml)
- [10 · 01 — Academia de Hektor Profe](../10%20-%20Cursos%20en%20español/01%20-%20Academia%20de%20Hektor%20Profe.md) —
  curso 7 (beat 'em up, 5 lecciones) y curso 6 (Action RPG, con estado de ataque y colisiones).
- [12 · 06 — itch.io](../12%20-%20Utilidades%20e%20integraciones/06%20-%20itch.io%20-%20assets,%20herramientas%20y%20jams.md) —
  el proyecto *Hitboxes and Hurtboxes* de ratcasket, gratis y con explicación.

---

## 9. Fuentes

**Vocabulario y diseño de combate** (todas consultadas el 2026-09-06):

- **The Fighting Game Glossary**, Infil — 1 010 términos. Es la referencia de facto del
  vocabulario. Consultadas las entradas *Hitbox*, *Hurtbox*, *Startup*, *Active*, *Recovery*,
  *Frame Data*, *Frame Advantage*, *Cancel*, *Hit Confirm*, *Armor*, *Juggle*,
  *Damage Scaling*, *Hit Stun*, *Block Stun*, *Hit Stun Deterioration*, *Priority System*,
  *Parry*, *Block*, *Counter Hit*, *Plus*, *Minus*, *Trade*, *Clash*, *Frame Trap*, *Buffer*,
  *Invincible*, *Strike Invincible*, *Throw Invincible*, *Launcher*, *Pushback*, *Okizeme* —
  https://glossary.infil.net/
- **Dustloop Wiki — Glossary** — la definición de *Startup* que fija la convención de contar
  el primer fotograma activo dentro del arranque —
  https://www.dustloop.com/w/Glossary
- ⚠️ **«*Devil May Cry 5*: Creating a Standout Action Game»**, GDC 2019 — Hideaki Itsuno
  (director), Michiteru Okabe (productor senior), Matt Walker (productor). **No he visto la
  charla**: sólo el anuncio oficial de GDC, que resume el enfoque de Itsuno como «trabajar
  hacia atrás desde un objetivo de experiencia del jugador». La cito como pista, no como
  fuente de los números de este documento —
  https://gdconf.com/article/devil-may-cry-5-director-shares-capcom-s-stylish-action-game-formula-at-gdc-2019/ ·
  ficha en GDC Vault: https://www.gdcvault.com/play/1025764/-Devil-May-Cry-5

**Implementaciones en GameMaker:**

- **HitBoxes_gml**, MichelVGameMaker — librería para GameMaker Studio 2 que gestiona hitboxes
  y hurtboxes. De ella viene el parámetro `set_rehurt_timing()` («el tiempo transcurrido
  necesario, en steps, para que la hitbox hiera dos veces a la misma entidad») y la idea de
  que la caja siga al dueño replicando su escala y su ángulo. Licencia: «G2L is fully free» —
  https://github.com/MichelVGameMaker/HitBoxes_gml
- **Hitboxes and Hurtboxes**, ratcasket (itch.io) — proyecto de ejemplo gratuito, ya catalogado
  en [12 · 06](../12%20-%20Utilidades%20e%20integraciones/06%20-%20itch.io%20-%20assets,%20herramientas%20y%20jams.md) —
  https://ratcasket.itch.io/hitboxes-and-hurtboxes

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`):

- `rectangle_in_rectangle` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/rectangle_in_rectangle.htm
- `collision_rectangle` y `collision_rectangle_list` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/collision_rectangle_list.htm
- `instance_place_list` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_place_list.htm
- `instance_create_layer` (con struct de variables) —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_create_layer.htm
- `is_debug_overlay_open` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Debugging/is_debug_overlay_open.htm
- Orden de los eventos (Begin Step / Step / End Step) —
  https://manual.gamemaker.io/lts/es/The_Asset_Editors/Object_Properties/Object_Events.htm

> ⚠️ **Lo que NO está verificado en este documento.** Todos los símbolos de GML usados existen
> en el runtime 2026.0.0.23 (comprobados con `_indice/buscar.py`), pero **el código no se ha
> compilado ni ejecutado en un proyecto real**: los nombres de sprites, sonidos y objetos
> (`spr_jugador_ligero_1`, `snd_espada_ligero`, `obj_solido`…) son marcadores de posición que
> tienes que crear. Los **números de frame data** (arranques de 4, 11 y 26 fotogramas,
> hitstun de 14, escalado de daño) son un punto de partida razonable tomado de las
> convenciones del género, **no medidas de ningún juego concreto**: ajústalos jugando.
