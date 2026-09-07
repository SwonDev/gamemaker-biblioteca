# 32 · Sistema de daño y efectos de estado

> **Dificultad:** media-alta · **Antes de esto:** el sistema de hitboxes/hurtboxes de
> [04 · 30](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md)
> funcionando, con `EstadoCombate` y `recibir_golpe()` ya en marcha: **este documento no
> sustituye ese sistema, lo amplía.**
> El paquete de datos que decide **cuánto duele de verdad un golpe** —tipo de daño y
> resistencias, armadura, escudos— y **qué le pasa a quien lo recibe después** —veneno,
> quemadura, congelación, aturdimiento, ralentización, regeneración— con un único motor de
> efectos de estado en vez de una variable suelta por efecto.
>
> **Qué NO cubre este documento** (y dónde está): las cajas de golpe, el *frame data*, los
> combos y el *hitstun* del propio impacto viven en
> [04 · 30](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md);
> aquí se **usa** ese `recibir_golpe()`, no se reescribe. El empuje, el *hit stop*, la sacudida
> de cámara, las partículas y el texto flotante son de
> [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md). El crítico con piedad
> (*pity*) es de
> [13 · 13 §5.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md).
> La barra de vida del jugador (la barra «fantasma») es de
> [13 · 05 §3.5 b)](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md).
> El TTK/DPS de **diseño**, la hoja de cálculo de balance y el Debug Overlay son de
> [13 · 01 §4.4 y §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md).
> Lo que **tampoco** cubre: los **arquetipos de enemigo**, la **tabla de amenaza** (*aggro*) y el
> **director de intensidad** de un encuentro, que son de
> [04 · 33](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
> (§1, §4 y §5-6 respectivamente).

---

## 1. Los principios

### 1.1 El pipeline de daño: cinco capas, en un orden que importa

Un golpe no resta vida directamente. Pasa por capas, y **el orden decide el resultado**: aplicar
la armadura antes que la resistencia no es lo mismo que al revés si alguna es multiplicativa.
Este documento fija un orden y se atiene a él:

| # | Capa | Qué hace | Dónde vive |
|---|---|---|---|
| 1 | Daño base + crítico + escalado de combo | El número que sale del arma/ataque | `_caja.dano` (04 · 30 §5.1) × `escalado_de_dano()` (04 · 30 §5.7) × crítico (13 · 13 §5.7) |
| 2 | **Tipo de daño → resistencia** | Multiplica por la tabla de la víctima. `0` = inmune, `1` = normal, `>1` = débil, `<0` = absorbe y cura | §4.1 de este documento |
| 3 | **Armadura** | Reducción plana o porcentual, con penetración | §4.2 |
| 4 | **Escudo** | Absorbe lo que le cabe antes de tocar la vida | §4.3 |
| 5 | Vida | Lo que sobra de las cuatro capas anteriores | `combate.vida` (04 · 30 §6) |

El daño **verdadero** (`DanoTipo.VERDADERO`, típico de guiones, caídas al vacío o el «suelo es
lava») se salta las capas 2-4 a propósito: nunca lo mitiga nada.

### 1.2 El triángulo elemental como generador de decisiones

Un sistema de tipos con fortalezas y debilidades cruzadas no es decoración: es lo que convierte
«pulsar atacar» en «elegir el arma correcta». El ejemplo mejor documentado de la industria es
el de *Pokémon*, con tres reglas fijas y sin excepciones:

> «Si un movimiento es súper efectivo contra un tipo, el daño se dobla (2×). Si es poco
> efectivo, se parte por la mitad (0,5×). Si no tiene efecto, el objetivo es completamente
> inmune y el movimiento no hace daño (0×).» Con dos tipos a la vez, los multiplicadores **se
> multiplican entre sí**: súper efectivo contra los dos da 4× de daño; poco efectivo contra los
> dos, sólo ¼.

Esa regla —multiplicar, no sumar— es la razón de que `resistencia_obtener()` (§4.1) devuelva un
factor y no una resta: sumar resistencias de fuego y hielo daría números que no se leen; multi-
plicarlas da un 0,25× o un 4× que el jugador puede aprender a predecir.

⚠️ El argumento de que un triángulo elemental crea «decisiones significativas» en el sentido
de diseño de Sylvester (*Designing Games*) es una idea consolidada de la disciplina, pero no he
abierto el libro en esta sesión: cítalo como criterio de diseño, no como cifra verificada.

### 1.3 Reducción de daño: plana o porcentual, y por qué escalan distinto

Hay dos familias de armadura y no son intercambiables:

- **Plana** (`daño − armadura`): fácil de leer («20 de armadura son 20 de daño menos»), pero
  un arma floja **deja de hacer daño del todo** contra armadura alta, y una vida que sube con
  el nivel vuelve la armadura plana irrelevante en las últimas horas de juego.
- **Porcentual**, a la manera de *League of Legends*: cada punto de armadura añade una fracción
  de **vida efectiva**, nunca la anula del todo. La wiki oficial lo define así:
  > «El daño físico final es `daño × 100 / (100 + Armadura)`. Cada punto de armadura añade
  > aproximadamente un 1 % de vida efectiva frente al daño físico.»
  Con 100 de armadura, el daño físico se parte exactamente por la mitad; con 400, se reduce a
  la quinta parte. Nunca llega a cero: siempre hay un porcentaje que pasa.

La **penetración** (plana o porcentual) es lo que le da textura al armamento pesado: un arma
que ignora una parte de la armadura antes de aplicar la fórmula sigue siendo débil contra un
objetivo desarmado y fuerte contra uno acorazado — la decisión de equipo vuelve a importar.

### 1.4 Escudos: un amortiguador, no una segunda barra de vida

Un escudo que se regenera **al instante** no aporta nada: el jugador nunca lo ve romperse. La
convención que fijó el género —los escudos de *Halo*— añade justo lo que falta: una **capa de
absorción** delante de la vida y un **retardo** antes de regenerar, que varía por entrega:

> «Los escudos de *Halo: Combat Evolved* comienzan a regenerarse 5 segundos después de recibir
> el último golpe; en *Halo 2* el retardo baja a 4,25 segundos; en *Halo 3* vuelve a 5.»

El número exacto es lo de menos (ajústalo jugando, como el resto del *frame data* de esta
biblioteca): lo que importa es la **estructura** — capacidad, retardo tras el último golpe,
regeneración progresiva y un evento de «ruptura» con su propio *feedback* — que es la de §4.3.

### 1.5 Efectos de estado: por qué son structs con un tic, no variables sueltas

`envenenado = true; veneno_tiempo = 180;` funciona para un efecto. Con cinco, y dos fuentes de
veneno simultáneas, y un enemigo inmune al veneno pero no al fuego, deja de funcionar: son
`if` anidados que nadie quiere depurar. La solución, consistente con `EstadoCombate` de
[04 · 30 §6](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md#6-gestión-del-estado-de-combate),
es la misma: **un struct por efecto activo, en un array, con un tic por fotograma** (§4.4).

Tres decisiones de diseño que hay que tomar ANTES de escribir el motor, porque cambian el
resultado:

| Política de apilado | Qué pasa al reaplicar | Cuándo usarla |
|---|---|---|
| **Renovar** | La duración vuelve al máximo; la intensidad no cambia | Quemadura, aturdimiento: un segundo golpe de fuego no debe quemar el doble |
| **Apilar** | Se suma una pila (hasta un tope) y la duración se renueva | Veneno, ralentización: cada golpe adicional empeora el efecto |
| **Máximo** | Se queda con la duración más larga de las dos, sin sumar intensidad | Efectos binarios (invulnerable/no) donde apilar no tiene sentido |

Y una tabla de decaimiento del daño por tic es un patrón real, no una ocurrencia: el veneno de
*Old School RuneScape* reduce su propia severidad en cada tic:

> «El veneno inflige daño una vez cada 30 *game ticks* (18 segundos). La severidad decrece en 1
> cada vez que se inflige daño, y el daño mostrado baja en 1 cada 5 aplicaciones, hasta que la
> severidad llega a 0 y el efecto termina.»

§4.5 usa la variante más simple de esa idea (daño fijo por pila, sin decaimiento) porque encaja
mejor con el «apilar» de un ARPG en tiempo real; el decaimiento por tic es la mejora natural
cuando el veneno deba sentirse como una amenaza que se apaga sola.

### 1.6 Comunicar el daño y el estado, no sólo aplicarlo

Un jugador que no sabe *por qué* un golpe hizo poco daño cree que el juego está roto, no que el
enemigo resiste el fuego. Tres canales, del más barato al más caro:

1. **Color** del número flotante y del contorno del enemigo, por tipo de daño (§4.6).
2. **Icono con contador de pilas** por cada efecto activo, en una fila fija (§4.6).
3. **Texto explícito** sólo para lo que de verdad sorprende («¡Inmune!», «¡Débil al fuego!»):
   spamear texto por cada golpe normal es ruido, no información.

### 1.7 Subgéneros: qué cambia

| Subgénero | Qué pesa más aquí | Ejemplo de tabla de datos |
|---|---|---|
| Action RPG / *Souls-like* | Armadura porcentual + penetración; escudo poco común, estamina sí (fuera de alcance: [04 · 04](./04%20-%20RPG%20_%20Action%20RPG.md)) | `armadura: 45, penetracion_arma: 0.15` |
| JRPG por turnos | Tabla de resistencias por tipo, explícita en el menú («débil al hielo») | `resistencias: { fuego: 1.5, hielo: 0.25 }` |
| Roguelike de acción | Apilado agresivo de DoT de fuentes distintas; efectos de rareza alta que rompen la regla general | `veneno.pilas_max: 20` en una build de veneno |
| Tower Defense | Resistencia por tipo de torre, leída de datos por oleada (`04 · 08 §8`, hoy sin implementar) | `resistencias: { area: 0.5, hielo: 0 }` |
| Shooter / MOBA | Armadura porcentual como la única capa; sin efectos de estado complejos, sólo aturdimientos cortos | `armadura: 30` |

---

## 2. Arquitectura recomendada

### 2.1 Dónde vive cada cosa

Nada de esto sustituye `EstadoCombate`: **cuelga de él**, como campos añadidos tras construirlo
(GML permite añadir campos a un struct en cualquier momento):

```gml
combate = new EstadoCombate(2, 100);       // 04 · 30 §6 — sin tocar
combate.armadura     = 15;                 // NUEVO — §4.2
combate.resistencias = { fuego: 1.5 };     // NUEVO, opcional — §4.1
combate.escudo       = new Escudo(40, 90, 0.6);   // NUEVO — §4.3
combate.efectos      = new MotorEfectos(combate); // NUEVO — §4.4
combate.bloqueo_curacion = 0;              // NUEVO — §4.7
```

Un enemigo sin `armadura` ni `resistencias` sigue funcionando exactamente igual que hoy: todas
las comprobaciones son `variable_struct_exists()` con una salida neutra. **Esto es a propósito**:
puedes añadir el sistema a un proyecto que ya tiene combate sin tocar los enemigos existentes.

### 2.2 El paquete que viaja: dos campos nuevos en la caja de golpe

`recibir_golpe()` (04 · 30 §5.7) ya recibe un `_golpe = { caja, atacante, victima, direccion }`.
Este documento añade dos campos **opcionales** a `_caja` (la entrada de `global.ataques`):

```gml
caja : { dx: 22, dy: -12, ancho: 30, alto: 24 },
dano : 18,
tipo : DanoTipo.FUEGO,        // NUEVO. Si falta, se asume DanoTipo.FISICO (§4.1)
penetracion : 0.30,           // NUEVO. Si falta, se asume 0 (§4.2)
```

Cero ataques existentes se rompen: los dos campos son opcionales y `dano_resolver()` (§4.1)
los rellena con el valor neutro si no están.

### 2.3 Política de apilado como enumeración, no como booleano

`enum PoliticaApilado { RENOVAR, APILAR, MAXIMO }` en vez de un `bool se_apila` porque la
tercera opción (§1.5) no es «sí o no»: es una tercera familia de comportamiento, y un booleano
no la puede representar sin un segundo booleano al lado — la señal de que hace falta un enum.

---

## 3. El bucle central: el orden de los tics

**El orden en el `Step` importa tanto como el pipeline de daño.** Los efectos de estado deben
seguir avanzando aunque la entidad esté aturdida —un veneno no se detiene porque te hayan
golpeado—, así que su `tick()` va **antes** del corte por `tiene_control()`, no después:

```gml
// ---------------------------------------------------------------------------
// obj_entidad — Step (amplía 04 · 30 §6, que hoy sólo tiene las líneas marcadas)
// ---------------------------------------------------------------------------
combate.tick();                              // 04 · 30 §6 — sin tocar
combate.efectos.tick();                      // NUEVO — sigue corriendo en hitstun
combate.escudo.tick();                       // NUEVO — la regeneración no depende del control
if (combate.bloqueo_curacion > 0) combate.bloqueo_curacion--;   // NUEVO

if (!combate.tiene_control())                // 04 · 30 §6 — sin tocar
{
    vel_x = lerp(vel_x, 0, 0.18);
    exit;
}

vel_x *= combate.efectos.multiplicador_velocidad();   // NUEVO — congelación / ralentización

image_alpha = (combate.iframes > 0 && (combate.iframes div 3) % 2 == 0) ? 0.35 : 1;   // 04 · 30 §6

if (combate.vida <= 0 && !fsm.is("muerto")) fsm.set("muerto");   // 04 · 30 §6
```

🔺 **Si mueves `combate.efectos.tick()` DESPUÉS del `exit`**, el veneno deja de hacer daño
mientras el objetivo está aturdido — y un enemigo que encadena aturdimientos cortos se vuelve
inmune de facto a cualquier daño con el tiempo. Es el error más fácil de cometer al enganchar
esto: la posición de esa línea es la parte que de verdad importa de esta sección.

---

## 4. Sistemas clave

### 4.1 Tipos de daño y tabla de resistencias

Ocho tipos, uno de ellos especial (`VERDADERO`, §1.1). La tabla de resistencias de cada entidad
es un struct plano — el mismo formato que ya usa `04 · 08` para su idea pendiente de
resistencias, así que si ese documento llega a implementarlo, comparte formato con este:

```gml
resistencias = { fuego: 1.5, hielo: 0.5, veneno: 0, sagrado: -0.5 };
// Fuego: débil (50 % más de daño). Hielo: resiste la mitad. Veneno: inmune.
// Sagrado: NEGATIVO → en vez de dañar, CURA (absorción invertida, §4.1).
```

Los tipos que faltan en la tabla valen `1.0` (daño normal): no hace falta rellenar los ocho.

### 4.2 Armadura: plana, porcentual y penetración

Elige una familia por proyecto (mezclar las dos en el mismo enemigo es la fila 4 de §7). La
porcentual (§1.3) es la recomendada por defecto: escala bien y nunca deja un arma en cero.

### 4.3 Escudos: absorción, retardo de regeneración y ruptura

Delante de la vida, no encima. Tres estados observables: **lleno** (absorbe todo lo que puede),
**agotándose** (absorbe parcialmente, el resto llega a la vida) y **roto** (ya no absorbe nada
hasta que pasa el retardo sin recibir golpes). El evento de ruptura es el enganche para tu
propio *feedback* — sonido, flash, un frame de invulnerabilidad de gracia — no algo que este
documento imponga.

### 4.4 El motor de efectos de estado

Un `MotorEfectos` por entidad, colgado de `combate.efectos` (§2.1). Guarda una lista de
efectos activos (`{ id, def, pilas, restante, duracion_total, tic_restante }`) y una lista de
inmunidades temporales tras la expiración natural de un efecto — necesaria para que un
aturdimiento no se pueda reencadenar sin ventana (la queja más común del género: el «combo de
aturdimiento infinito»).

### 4.5 Efectos concretos: veneno, quemadura, congelación, aturdimiento, ralentización

Cinco instancias de datos sobre el mismo motor, más una sexta (`regeneracion`, §4.7) que
demuestra que el motor sirve igual para curar que para dañar: **es el mismo bucle, con el signo
cambiado.**

| Efecto | Política | Qué hace | Corta el control? |
|---|---|---|---|
| Veneno | Apilar (máx. 5) | DoT fijo por pila, cada segundo | No |
| Quemadura | Renovar | DoT fijo, no escala con reaplicar | No |
| Congelación | Máximo | `multiplicador_velocidad()` a 0 | No (es lento, no ciego) |
| Aturdimiento | Renovar, con inmunidad tras expirar | Corta el control vía `tiene_control()` | **Sí** |
| Ralentización | Apilar (máx. 2) | `multiplicador_velocidad()` reducido por pila | No |
| Regeneración | Apilar (máx. 3) | HoT fijo por pila | No |

### 4.6 Comunicar el daño y los estados al jugador

Un color por tipo (tabla `global.dano_tipo_info`, ya indexable por `DanoTipo`) reutilizado en
tres sitios: el número flotante de 04 · 15 §5.6, el contorno o *tint* del sprite al recibir el
golpe, y el icono del propio efecto de estado. Una única fuente de verdad para el color evita
que el número flotante diga «fuego» en amarillo y el icono lo pinte de rojo.

**Congelación, como efecto visual compuesto — no hace falta técnica nueva.** El tinte plano de
arriba (`global.dano_tipo_info[DanoTipo.HIELO].color`) ya se aplica al icono y al número
flotante; en el propio sprite se lee mejor combinado con la desaturación progresiva de
[08 · 06 §6.1](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#61-desaturación-progresiva) —
el gris drena «vida» del sprite antes de sumarle el azul, en vez de un tinte plano sobre los
colores originales:

```gml
// obj_enemigo — Draw, mientras combate.efectos.tiene("congelacion") (§5.4)
if (combate.efectos.tiene("congelacion"))
{
    shader_set(sh_desaturar);                          // 08 · 06 §6.1, tal cual
    shader_set_uniform_f(u_intensidad, 0.6);
    image_blend = merge_color(c_white, global.dano_tipo_info[DanoTipo.HIELO].color, 0.35);
    draw_self();
    shader_reset();
    image_blend = c_white;
}
else
{
    draw_self();
}
```

Para la escarcha creciendo encima (no solo el tinte), superpón una textura simple de cristales
con `bm_add` y alfa creciente según el tiempo que le queda al efecto — los mismos campos
`.restante`/`.duracion_total` de `combate.efectos.activos[i]` que ya usa §5.10 para la barra bajo
el icono, aplicados aquí a la opacidad de la escarcha en vez de a una barra.

**Quemado, igual de compuesto.** `pt_fuego`/`pt_ascua` de
[04 · 39 §3.1](./39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#31-ampliar-objfx-los-tipos-de-partícula-que-faltaban)
ya existen para fuego EN UN PUNTO fijo (una antorcha, §3.3 de ese documento); para un enemigo
que arde basta con crearlas desde su posición ACTUAL cada Step, no desde un emisor anclado:

```gml
// obj_enemigo — Step, mientras combate.efectos.tiene("quemadura")
if (combate.efectos.tiene("quemadura"))
{
    part_particles_create(objFx.ps, x, y - sprite_height * 0.5, objFx.pt_fuego, 1);
}
```

`part_type_step(pt_fuego, -6, pt_ascua)` — ya definido en esa misma sección de 04 · 39 — sigue
engendrando ascuas sin cambiar nada: el fuego «se mueve con el enemigo» porque el punto de
creación se recalcula cada frame con su propio `x, y`, no porque haya un sistema nuevo que
seguirlo.

### 4.7 Curación como sistema: HoT y el bloqueo en combate

Tres decisiones de diseño, no una: **cuándo** se puede curar (¿en pleno combo, como un JRPG, o
nunca, como un *soulslike*?), **cuánto tarda** (instantánea, como una poción, o repartida en el
tiempo, como una regeneración) y **cuánto cura de más** cuando ya está a tope (aquí, nada: el
`curar()` de `EstadoCombate` ya satura en `vida_max`; para sobrecuración real usa un `Escudo`
con `regen_por_frame: 0` — es exactamente una capa de vida extra que no se recarga sola).
El economista de recursos general —fuentes, sumideros, realimentación— está en
[13 · 01 §4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md);
aquí sólo se cubre el mecanismo, no la economía.

### 4.8 Barra de jefe segmentada por fases

Reutiliza `barra_nueva/fijar/actualizar/dibujar` de
[13 · 05 §3.5 b)](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md)
tal cual — no las reimplementa — y añade encima **una sola cosa**: el número de fase actual,
calculado a partir del `hp_threshold` que ya usa el jefe de
[04 · 03 §5.7](./03%20-%20Shoot%20em%20up%20%28shmup%29.md), y separadores verticales que marcan
dónde empieza cada fase.

---

## 5. Código base

### 5.0 Configuración (`scr_dano_config`)

```gml
// ---------------------------------------------------------------------------
// scr_dano_config — constantes del sistema de daño y efectos de estado.
// Asume que ya existe scr_combate_config (04 · 30 §5.0) y que TELEMETRIA_ACTIVA
// ya está definida (13 · 01 §9.5); si no usas telemetría, defínelo a `false` y
// §5.13 se apaga sola.
// ---------------------------------------------------------------------------

#macro CURACION_BLOQUEO_FRAMES   90   // ~1,5 s a 60 fps tras recibir daño (§4.7)

// Duraciones por defecto de los efectos, en fotogramas a 60 fps. Que sean
// datos, no números sueltos en cada llamada a aplicar(), es lo que permite
// reequilibrar sin recompilar (04 · 30 §8, "Ataques en JSON" — mismo espíritu).
global.efecto_duracion = {
    veneno         : 300,   // 5 s
    quemadura      : 180,   // 3 s
    congelacion    : 90,    // 1,5 s
    aturdimiento   : 60,    // 1 s
    ralentizacion  : 240,   // 4 s
    regeneracion   : 300    // 5 s
};
```

### 5.1 Tipos de daño y tabla de resistencias

```gml
// ---------------------------------------------------------------------------
// scr_dano_tipos
// ---------------------------------------------------------------------------

/// Ocho tipos. VERDADERO se salta resistencia, armadura Y escudo (§1.1):
/// resérvalo para daño de guion, caída al vacío o "el suelo es lava".
enum DanoTipo { FISICO, FUEGO, HIELO, RAYO, VENENO, SAGRADO, OSCURO, VERDADERO }

/// Nombre, color e icono por tipo — una sola tabla para el número flotante,
/// el tinte del sprite y el icono de estado (§4.6). Rellena con tus sprites:
/// spr_icono_* son marcadores de posición, como el resto de sprites de esta
/// biblioteca (04 · 30 §9).
global.dano_tipo_info = [
    { nombre : "Físico",    color : c_white,  icono : spr_icono_fisico    },
    { nombre : "Fuego",     color : c_orange, icono : spr_icono_fuego     },
    { nombre : "Hielo",     color : c_aqua,   icono : spr_icono_hielo     },
    { nombre : "Rayo",      color : c_yellow, icono : spr_icono_rayo      },
    { nombre : "Veneno",    color : c_lime,   icono : spr_icono_veneno    },
    { nombre : "Sagrado",   color : c_white,  icono : spr_icono_sagrado   },
    { nombre : "Oscuro",    color : c_purple, icono : spr_icono_oscuro    },
    { nombre : "Verdadero", color : c_red,    icono : spr_icono_verdadero }
];

/// @func dano_tipo_a_clave(_tipo)
/// @desc DanoTipo → nombre de campo en español, para leer/escribir tablas de
///       datos y JSON (`resistencias.fuego`, no `resistencias[0]`).
/// @param {Real} _tipo  Un miembro de DanoTipo (VERDADERO no tiene clave: no
///                      se guarda en tablas de resistencia).
/// @returns {String}
function dano_tipo_a_clave(_tipo)
{
    switch (_tipo)
    {
        case DanoTipo.FISICO:  return "fisico";
        case DanoTipo.FUEGO:   return "fuego";
        case DanoTipo.HIELO:   return "hielo";
        case DanoTipo.RAYO:    return "rayo";
        case DanoTipo.VENENO:  return "veneno";
        case DanoTipo.SAGRADO: return "sagrado";
        case DanoTipo.OSCURO:  return "oscuro";
    }
    return "fisico";
}

/// @func resistencia_obtener(_tabla, _tipo)
/// @desc Multiplicador de daño para un tipo. 1.0 si el tipo no está en la
///       tabla: no hace falta rellenar los ocho campos en cada enemigo.
/// @param {Struct} _tabla  P. ej. { fuego: 1.5, hielo: 0.5, veneno: 0 }.
/// @param {Real}   _tipo   Un miembro de DanoTipo.
/// @returns {Real}  0 = inmune · 1 = normal · >1 = débil · <0 = absorbe y cura.
function resistencia_obtener(_tabla, _tipo)
{
    var _clave = dano_tipo_a_clave(_tipo);
    return variable_struct_exists(_tabla, _clave) ? _tabla[$ _clave] : 1.0;
}

/// @func resistencias_cargar(_archivo)
/// @desc Lee una tabla de resistencias desde un JSON de Included Files, con
///       el patrón de 01 · 14 §8 (buffer → string → json_parse). 40 enemigos
///       en datos es 40 archivos sin recompilar, no 40 ramas de código.
/// @param {String} _archivo  Ruta relativa al área de juego.
/// @returns {Struct}  {} si el archivo no existe (todo a 1.0, sin romper nada).
function resistencias_cargar(_archivo)
{
    if (!file_exists(_archivo)) return {};

    var _buff = buffer_load(_archivo);
    var _json = buffer_read(_buff, buffer_string);
    buffer_delete(_buff);

    return json_parse(_json);
}
```

```gml
// obj_enemigo_esqueleto · Create — dato puro, sin lógica
combate = new EstadoCombate(2, 40);
combate.resistencias = { fisico: 0.75, sagrado: 2.0, veneno: 0, oscuro: 0.5 };
// Exactamente el mismo struct que devolvería:
//   combate.resistencias = resistencias_cargar("data/resistencias_esqueleto.json");
```

### 5.2 Armadura

```gml
// ---------------------------------------------------------------------------
// scr_armadura
// ---------------------------------------------------------------------------

/// @func armadura_mitigar(_dano, _armadura, _penetracion_pct = 0, _penetracion_plana = 0)
/// @desc Reducción PORCENTUAL, a la manera de League of Legends: cada punto de
///       armadura añade 1/(100+armadura) de vida efectiva. Con 100 de armadura
///       el daño físico se parte por la mitad; nunca llega a cero (§1.3).
/// @param {Real} _dano
/// @param {Real} _armadura
/// @param {Real} _penetracion_pct    0..1. Reduce la armadura ANTES de la fórmula.
/// @param {Real} _penetracion_plana  Puntos de armadura ignorados, después del %.
/// @returns {Real}
function armadura_mitigar(_dano, _armadura, _penetracion_pct = 0, _penetracion_plana = 0)
{
    var _efectiva = max(0, _armadura * (1 - _penetracion_pct) - _penetracion_plana);
    return _dano * (100 / (100 + _efectiva));
}

/// @func armadura_mitigar_plana(_dano, _armadura)
/// @desc La alternativa simple: resta fija, nunca por debajo de 1 (§1.3).
/// @param {Real} _dano
/// @param {Real} _armadura
/// @returns {Real}
function armadura_mitigar_plana(_dano, _armadura)
{
    return max(1, _dano - _armadura);
}
```

### 5.3 Escudos

```gml
// ---------------------------------------------------------------------------
// scr_escudo
// ---------------------------------------------------------------------------

/// @func Escudo(_capacidad_max, _retardo_frames, _regen_por_frame)
/// @desc Capa de absorción DELANTE de la vida. `_retardo_frames` es cuánto
///       espera sin recibir golpes antes de regenerar (Halo: CE tarda 5 s =
///       300 F a 60 fps; ver §1.4 y Fuentes). `_regen_por_frame: 0` lo
///       convierte en una capa de vida extra que nunca se recarga sola —
///       útil para sobrecuración temporal (§4.7).
function Escudo(_capacidad_max, _retardo_frames, _regen_por_frame) constructor
{
    capacidad        = _capacidad_max;
    capacidad_max    = _capacidad_max;
    retardo_frames   = _retardo_frames;
    regen_por_frame  = _regen_por_frame;
    espera           = 0;
    roto             = false;

    /// @desc Absorbe lo que puede; devuelve el SOBRANTE que sí llega a la vida.
    /// @param {Real} _dano
    /// @returns {Real}
    static absorber = function(_dano)
    {
        if (capacidad <= 0) return _dano;

        var _absorbido = min(capacidad, _dano);
        capacidad -= _absorbido;
        espera = retardo_frames;

        if (capacidad <= 0 && !roto)
        {
            roto = true;
            // Enganche para tu feedback de ruptura: sonido, flash, invuln. de gracia.
        }
        return _dano - _absorbido;
    };

    /// @desc Un tic por fotograma. Llámalo junto a combate.tick() (§3).
    static tick = function()
    {
        if (espera > 0) { espera--; return; }
        if (capacidad < capacidad_max)
        {
            capacidad = min(capacidad_max, capacidad + regen_por_frame);
            if (capacidad > 0) roto = false;
        }
    };
}
```

### 5.4 El motor de efectos de estado

```gml
// ---------------------------------------------------------------------------
// scr_motor_efectos
// ---------------------------------------------------------------------------

enum PoliticaApilado { RENOVAR, APILAR, MAXIMO }

/// @func MotorEfectos(_combate)
/// @desc Uno por entidad, colgado de combate.efectos (§2.1). `_combate` es la
///       MISMA instancia de EstadoCombate a la que se cuelga: así on_tic() y
///       compañía pueden llamar a combate.curar() o leer combate.vida sin que
///       tú tengas que pasarlo cada vez.
function MotorEfectos(_combate) constructor
{
    combate     = _combate;
    activos     = [];   // { id, def, pilas, restante, duracion_total, tic_restante }
    inmunidades = [];   // { id, restante } — tras expirar un efecto con inmunidad

    /// @func aplicar(_id, _duracion_frames)
    /// @desc Añade el efecto, o lo renueva/apila/extiende según su política.
    /// @param {String} _id              Clave en global.EFECTOS_DEF.
    /// @param {Real}   _duracion_frames
    static aplicar = function(_id, _duracion_frames)
    {
        if (esta_inmune(_id)) return;

        var _def = global.EFECTOS_DEF[$ _id];
        if (_def == undefined)
        {
            show_debug_message($"[efectos] '{_id}' no existe en EFECTOS_DEF — revisa el id");
            return;
        }

        for (var i = 0; i < array_length(activos); i++)
        {
            if (activos[i].id != _id) continue;

            switch (_def.politica)
            {
                case PoliticaApilado.RENOVAR:
                    activos[i].restante = _duracion_frames;
                    break;
                case PoliticaApilado.APILAR:
                    activos[i].pilas    = min(activos[i].pilas + 1, _def.pilas_max);
                    activos[i].restante = _duracion_frames;
                    break;
                case PoliticaApilado.MAXIMO:
                    activos[i].restante = max(activos[i].restante, _duracion_frames);
                    break;
            }
            activos[i].duracion_total = max(activos[i].duracion_total, _duracion_frames);
            return;
        }

        // Primera vez que se aplica: entrada nueva.
        array_push(activos, {
            id : _id, def : _def, pilas : 1,
            restante : _duracion_frames, duracion_total : _duracion_frames,
            tic_restante : _def.tic_frames
        });

        if (variable_struct_exists(_def, "on_aplicar")) _def.on_aplicar(combate);
    };

    /// @desc Un tic por fotograma. Llámalo ANTES del corte por tiene_control() (§3).
    static tick = function()
    {
        for (var i = array_length(inmunidades) - 1; i >= 0; i--)
        {
            inmunidades[i].restante--;
            if (inmunidades[i].restante <= 0) array_delete(inmunidades, i, 1);
        }

        for (var i = array_length(activos) - 1; i >= 0; i--)
        {
            var _ef = activos[i];

            if (_ef.def.tic_frames > 0)
            {
                _ef.tic_restante--;
                if (_ef.tic_restante <= 0)
                {
                    _ef.def.on_tic(combate, _ef.pilas);
                    _ef.tic_restante = _ef.def.tic_frames;
                }
            }

            _ef.restante--;
            if (_ef.restante <= 0)
            {
                if (variable_struct_exists(_ef.def, "on_quitar")) _ef.def.on_quitar(combate);

                if (variable_struct_exists(_ef.def, "inmunidad_frames") && _ef.def.inmunidad_frames > 0)
                {
                    array_push(inmunidades, { id : _ef.id, restante : _ef.def.inmunidad_frames });
                }

                array_delete(activos, i, 1);
            }
        }
    };

    /// @func tiene(_id)
    /// @returns {Bool}
    static tiene = function(_id)
    {
        for (var i = 0; i < array_length(activos); i++)
        {
            if (activos[i].id == _id) return true;
        }
        return false;
    };

    /// @func quitar(_id)
    /// @desc Lo retira ANTES de tiempo (un objeto de "curar estado", un altar).
    ///       No concede inmunidad: quitar no es lo mismo que expirar.
    static quitar = function(_id)
    {
        for (var i = array_length(activos) - 1; i >= 0; i--)
        {
            if (activos[i].id != _id) continue;
            if (variable_struct_exists(activos[i].def, "on_quitar")) activos[i].def.on_quitar(combate);
            array_delete(activos, i, 1);
            return;
        }
    };

    /// @desc Llámalo al morir: no tiene sentido seguir tiqueando un cadáver.
    static limpiar = function()
    {
        activos = [];
    };

    /// @func esta_inmune(_id)
    /// @returns {Bool}
    static esta_inmune = function(_id)
    {
        for (var i = 0; i < array_length(inmunidades); i++)
        {
            if (inmunidades[i].id == _id) return true;
        }
        return false;
    };

    /// @func multiplicador_velocidad()
    /// @desc Léelo en tu propio Step: `vel_x *= combate.efectos.multiplicador_velocidad();`
    /// @returns {Real}  0 = inmóvil (congelación gana siempre sobre ralentización).
    static multiplicador_velocidad = function()
    {
        var _mult = 1;
        for (var i = 0; i < array_length(activos); i++)
        {
            if (activos[i].id == "congelacion")   return 0;
            if (activos[i].id == "ralentizacion") _mult *= (1 - 0.35 * activos[i].pilas);
        }
        return max(0, _mult);
    };

    /// @desc Struct plano para el guardado (§5.12). Las inmunidades NO se
    ///       guardan a propósito: una carga de partida no debe heredar
    ///       ventanas de inmunidad de la sesión anterior.
    static serializar = function()
    {
        var _out = [];
        for (var i = 0; i < array_length(activos); i++)
        {
            array_push(_out, { id : activos[i].id, pilas : activos[i].pilas,
                                restante : activos[i].restante });
        }
        return _out;
    };

    /// @func deserializar(_datos)
    /// @param {Array<Struct>} _datos  Lo que devolvió serializar().
    static deserializar = function(_datos)
    {
        activos = [];
        for (var i = 0; i < array_length(_datos); i++)
        {
            var _d = _datos[i];
            var _def = global.EFECTOS_DEF[$ _d.id];
            if (_def == undefined) continue;   // el efecto se retiró entre versiones
            array_push(activos, { id : _d.id, def : _def, pilas : _d.pilas,
                                   restante : _d.restante, duracion_total : _d.restante,
                                   tic_restante : _def.tic_frames });
        }
    };
}
```

### 5.5 Los efectos concretos (la tabla de datos)

```gml
// ---------------------------------------------------------------------------
// scr_efectos_def — UNA tabla de datos, no seis ramas de if. Un efecto nuevo
// es una entrada más aquí, nunca una recompilación de MotorEfectos.
// Campos: nombre, icono, color, politica, pilas_max, tic_frames (0 = sin DoT),
//         on_tic(combate, pilas), on_aplicar(combate) y on_quitar(combate)
//         (los dos últimos, opcionales).
// ---------------------------------------------------------------------------
global.EFECTOS_DEF = {
    veneno : {
        nombre : "Veneno", icono : spr_icono_veneno, color : c_lime,
        politica : PoliticaApilado.APILAR, pilas_max : 5, tic_frames : 60,
        on_tic : function(_combate, _pilas) { _combate.vida = max(0, _combate.vida - 2 * _pilas); }
    },

    quemadura : {
        nombre : "Quemadura", icono : spr_icono_fuego, color : c_orange,
        politica : PoliticaApilado.RENOVAR, pilas_max : 1, tic_frames : 30,
        on_tic : function(_combate, _pilas) { _combate.vida = max(0, _combate.vida - 4); }
    },

    congelacion : {
        nombre : "Congelación", icono : spr_icono_hielo, color : c_aqua,
        politica : PoliticaApilado.MAXIMO, pilas_max : 1, tic_frames : 0
        // Sin on_tic: el efecto es multiplicador_velocidad() == 0 (§5.4).
    },

    aturdimiento : {
        nombre : "Aturdimiento", icono : spr_icono_rayo, color : c_yellow,
        politica : PoliticaApilado.RENOVAR, pilas_max : 1, tic_frames : 0,
        inmunidad_frames : 20   // sin esto, dos aturdidores encadenan control 0 para siempre
    },

    ralentizacion : {
        nombre : "Ralentización", icono : spr_icono_hielo, color : c_ltgray,
        politica : PoliticaApilado.APILAR, pilas_max : 2, tic_frames : 0
        // Sin on_tic: el efecto es multiplicador_velocidad() (§5.4).
    },

    regeneracion : {
        nombre : "Regeneración", icono : spr_icono_regeneracion, color : c_lime,
        politica : PoliticaApilado.APILAR, pilas_max : 3, tic_frames : 60,
        on_tic : function(_combate, _pilas) { _combate.curar(3 * _pilas); }   // 04 · 30 §6
    }
};
```

```gml
// Aplicar un efecto: siempre a través del motor, nunca tocando `activos` a mano.
victima.combate.efectos.aplicar("veneno", global.efecto_duracion.veneno);
```

### 5.6 Enganchar todo en la entidad (Create)

```gml
// ---------------------------------------------------------------------------
// obj_jugador / obj_enemigo_* — Create, junto al resto de 04 · 30 §5.3/§5.12
// ---------------------------------------------------------------------------
combate = new EstadoCombate(2, 100);          // 04 · 30 §6 — sin tocar
combate.armadura         = 15;                // §5.2. Omítelo si no usas armadura.
combate.escudo           = new Escudo(40, 90, 0.6);   // §5.3. Omítelo si no hay escudos.
combate.efectos          = new MotorEfectos(combate); // §5.4 — casi siempre lo quieres
combate.bloqueo_curacion = 0;                 // §5.9

// tiene_control() de 04 · 30 §6 no sabe nada de efectos: se lo enseñamos
// reemplazando el método EN ESTA INSTANCIA con method(), sin tocar el archivo
// donde vive EstadoCombate. Un aturdimiento por VENENO no debería existir
// (el veneno no aturde, §4.5), pero uno por HECHIZO sí debe cortar el control
// exactamente igual que un golpe.
combate.tiene_control = method(combate, function()
{
    return (hitstun <= 0) && (blockstun <= 0) && (vida > 0) && !efectos.tiene("aturdimiento");
});
```

### 5.7 `recibir_golpe()` extendido — dónde se engancha el pipeline

```gml
// ---------------------------------------------------------------------------
// scr_combate_recibir — SUSTITUYE al paso 5 de recibir_golpe() en 04 · 30 §5.7.
// Todo lo anterior (parry, bloqueo, aguante, contragolpe) y todo lo posterior
// (hitstun, empuje, juggle, i-frames, hit_complete) se queda EXACTAMENTE igual:
// sólo cambia cómo se calcula _dano antes de restarlo de combate.vida.
// ---------------------------------------------------------------------------

// --- 5. Daño, con tipo, resistencia, armadura y escudo ----------------------
var _mult   = escalado_de_dano(combate.combo_golpes) * (_contra ? 1.25 : 1.0);
var _bruto  = max(1, round(_caja.dano * _mult));   // el bruto SIEMPRE es ≥ 1: el crítico
                                                     // y el escalado no deben poder anularlo.

// Dos campos NUEVOS y opcionales en la tabla de ataques (§2.2): si el ataque
// no los define, se comporta exactamente como antes de este documento.
var _tipo        = variable_struct_exists(_caja, "tipo")        ? _caja.tipo        : DanoTipo.FISICO;
var _penetracion = variable_struct_exists(_caja, "penetracion") ? _caja.penetracion : 0;

var _final = dano_resolver(_bruto, _tipo, _penetracion, combate);

combate.vida         -= _final;
combate.combo_golpes += 1;
combate.combo_olvido  = COMBO_OLVIDO_FRAMES;
combate.bloqueo_curacion = CURACION_BLOQUEO_FRAMES;   // §5.9

// Registro para depuración y balance — §5.13.
if (TELEMETRIA_ACTIVA)
{
    var _origen_nombre = instance_exists(_golpe.atacante)
        ? object_get_name(_golpe.atacante.object_index) : "desconocido";

    telemetria_registrar("golpe", {
        origen : _origen_nombre, objetivo : object_get_name(object_index),
        tipo : dano_tipo_a_clave(_tipo), bruto : _bruto, neto : _final,
        vida_restante : combate.vida
    });
}
```

```gml
/// @func dano_resolver(_bruto, _tipo, _penetracion, _combate)
/// @desc El pipeline de §1.1, capas 2-4. Se llama DESDE recibir_golpe(), con
///       `combate` ya resuelto por el `with (victima)` de 04 · 30 §5.7.
/// @param {Real}   _bruto        Ya con crítico y escalado de combo aplicados.
/// @param {Real}   _tipo         Un miembro de DanoTipo.
/// @param {Real}   _penetracion  0..1, penetración porcentual de armadura.
/// @param {Struct} _combate      La instancia de EstadoCombate de la víctima.
/// @returns {Real}  Daño neto a restar de _combate.vida. Puede ser 0 (inmune).
function dano_resolver(_bruto, _tipo, _penetracion, _combate)
{
    var _dano = _bruto;

    // El daño VERDADERO ignora las tres capas siguientes (§1.1).
    if (_tipo == DanoTipo.VERDADERO) return round(_dano);

    // 1 · Tipo y resistencia.
    if (variable_struct_exists(_combate, "resistencias"))
    {
        _dano *= resistencia_obtener(_combate.resistencias, _tipo);
    }
    if (_dano <= 0) return max(_dano, 0);   // inmune (0) o absorbe-y-cura (negativo, §4.1):
                                             // NUNCA se fuerza aquí un mínimo de 1 (ver 🔺 abajo).

    // 2 · Armadura, sólo contra daño físico: el fuego no lo detiene una coraza.
    if (_tipo == DanoTipo.FISICO && variable_struct_exists(_combate, "armadura"))
    {
        _dano = armadura_mitigar(_dano, _combate.armadura, _penetracion);
    }

    // 3 · Escudo: absorbe antes que la vida.
    if (variable_struct_exists(_combate, "escudo"))
    {
        _dano = _combate.escudo.absorber(_dano);
    }

    return max(0, round(_dano));
}
```

🔺 **El `max(1, …)` de `recibir_golpe()` (04 · 30 §5.7) garantiza que TODO golpe hace al menos 1
de daño — y sigue haciéndolo aquí, pero sólo sobre `_bruto`, ANTES de la resistencia.** Si ese
mínimo se aplicara también DESPUÉS de la resistencia, ningún enemigo podría ser inmune de
verdad: un `0` se convertiría en `1` y la tabla de resistencias mentiría. `dano_resolver()`
devuelve `0` sin corregirlo a propósito: la inmunidad tiene que poder llegar a cero.

Una resistencia **negativa** (`sagrado: -0.5` en el ejemplo de §5.1) hace que `_dano` se vuelva
negativo en el paso 1; si quieres que eso **cure** en vez de simplemente no dañar, añade antes
del `return`:

```gml
if (_dano < 0) { _combate.curar(-_dano); return 0; }   // absorbe e invierte el golpe en vida
```

### 5.8 Combinar con `hit_complete()` de 04 · 15: quién hace qué

`hit_complete(_victima, _dano, _direccion)` (04 · 15 §5.7) es un ejemplo **genérico** que
también resta vida y aplica su propio empuje — pensado para un proyecto que NO tiene todavía
`recibir_golpe()`. Si vienes de aquí, esas dos cosas **ya están hechas** en el paso 5-6 de
`recibir_golpe()` (04 · 30 §5.7): llamar a `hit_complete()` entero volvería a restar vida y a
empujar por segunda vez. Usa sólo las piezas de sensación que te falten:

```gml
// --- 8. Toda la sensación, MENOS el daño y el empuje (ya aplicados arriba) --
hit_stop(clamp(round(_final * 0.25), 1, 8));           // 04 · 15 §5.0
camera_shake(clamp(_final * 0.012, 0.08, 0.45));       // 04 · 15 §5.1
fx_floating_text(x, y - 16, string(_final), color_por_tipo(_tipo));   // §5.10, no c_yellow fijo
```

### 5.9 Curación como sistema: HoT y el bloqueo en combate

```gml
// ---------------------------------------------------------------------------
// scr_curacion
// ---------------------------------------------------------------------------

/// @func curacion_permitida(_combate)
/// @desc false justo después de recibir daño (§5.7 fija bloqueo_curacion).
///       Ponlo a 0 fotogramas en un JRPG por turnos, donde SÍ debe poder
///       curarse en pleno combate: es un dato de diseño, no una regla fija.
function curacion_permitida(_combate)
{
    return _combate.bloqueo_curacion <= 0;
}
```

```gml
// obj_item_pocion — al usarse
if (curacion_permitida(obj_jugador.combate))
{
    obj_jugador.combate.curar(30);
}
else
{
    fx_floating_text(obj_jugador.x, obj_jugador.y - 16, "¡No en combate!", c_gray);   // 04 · 15 §5.6
}

// Curación repartida en el tiempo: es sólo otra entrada del mismo motor (§5.5).
obj_jugador.combate.efectos.aplicar("regeneracion", global.efecto_duracion.regeneracion);
```

### 5.10 Comunicar al jugador: color por tipo y fila de iconos

```gml
// ---------------------------------------------------------------------------
// scr_dano_ui
// ---------------------------------------------------------------------------

/// @func color_por_tipo(_tipo)
/// @returns {Constant.Color}
function color_por_tipo(_tipo)
{
    return global.dano_tipo_info[_tipo].color;
}

/// @func efectos_dibujar_fila(_motor, _px, _py, _sep)
/// @desc Un icono por efecto activo, con el contador de pilas si hay más de
///       una, y una barra fina debajo con el tiempo restante — se lee de un
///       vistazo, sin números. Dibújalo en el Draw GUI, sobre la cabeza o en
///       el HUD (13 · 05 §3.5 tiene el resto de componentes de UI).
/// @param {Struct} _motor  combate.efectos
function efectos_dibujar_fila(_motor, _px, _py, _sep)
{
    var _x = _px;
    for (var i = 0; i < array_length(_motor.activos); i++)
    {
        var _ef = _motor.activos[i];

        draw_sprite_ext(_ef.def.icono, 0, _x, _py, 1, 1, 0, _ef.def.color, 1);

        if (_ef.pilas > 1)
        {
            draw_set_color(c_white);
            draw_text(_x + 10, _py + 6, string(_ef.pilas));
        }

        var _prop = _ef.restante / _ef.duracion_total;
        draw_rectangle_color(_x - 8, _py + 14, _x - 8 + 16 * _prop, _py + 16,
                             c_white, c_white, c_white, c_white, false);

        _x += _sep;
    }
}
```

### 5.11 Barra de jefe segmentada por fases

```gml
// ---------------------------------------------------------------------------
// scr_barra_jefe — envuelve barra_* de 13 · 05 §3.5 b), no las reimplementa.
// ---------------------------------------------------------------------------

/// @func barra_jefe_nueva(_maximo, _n_fases, _nombre)
function barra_jefe_nueva(_maximo, _n_fases, _nombre)
{
    return { barra : barra_nueva(_maximo), n_fases : _n_fases,
             fase_actual : _n_fases, nombre : _nombre };
}

/// @func barra_jefe_fijar(_bj, _valor)
function barra_jefe_fijar(_bj, _valor)
{
    barra_fijar(_bj.barra, _valor);
    var _umbral = _bj.barra.maximo / _bj.n_fases;
    _bj.fase_actual = max(1, ceil(_valor / _umbral));
}

/// @func barra_jefe_actualizar(_bj)
function barra_jefe_actualizar(_bj)
{
    barra_actualizar(_bj.barra);
}

/// @func barra_jefe_dibujar(_bj, _px, _py, _ancho, _alto)
function barra_jefe_dibujar(_bj, _px, _py, _ancho, _alto)
{
    barra_dibujar(_bj.barra, _px, _py, _ancho, _alto);

    // Un separador por umbral de fase: el jugador VE dónde empieza cada una.
    for (var i = 1; i < _bj.n_fases; i++)
    {
        var _x = _px + _ancho * (i / _bj.n_fases);
        draw_line_color(_x, _py, _x, _py + _alto, c_black, c_black);
    }

    draw_set_color(c_white);
    draw_text(_px, _py - 18, $"{_bj.nombre} — Fase {_bj.fase_actual}/{_bj.n_fases}");
}
```

```gml
// obj_jefe · Create — reutiliza el hp_threshold que YA tiene el jefe de 04 · 03 §5.7
barra_jefe = barra_jefe_nueva(combate.vida_max, array_length(fases), "El Guardián");

// obj_jefe · Step
barra_jefe_fijar(barra_jefe, combate.vida);
barra_jefe_actualizar(barra_jefe);

// obj_jefe · Draw GUI
barra_jefe_dibujar(barra_jefe, 220, 24, 400, 20);
```

### 5.12 Serialización en el guardado

```gml
// Dentro de guardar_partida() (01 · 14 §9), en el struct `jugador`:
jugador : {
    // … x, y, vida, vida_max, nivel (ya existentes) …
    armadura : obj_jugador.combate.armadura,
    escudo   : variable_struct_exists(obj_jugador.combate, "escudo")
                   ? obj_jugador.combate.escudo.capacidad : 0,
    efectos  : obj_jugador.combate.efectos.serializar()
}
```

```gml
// Dentro de cargar_partida(), tras validar `_datos` (01 · 14 §9):
obj_jugador.combate.armadura         = _datos.jugador.armadura;
obj_jugador.combate.escudo.capacidad = _datos.jugador.escudo;
obj_jugador.combate.efectos.deserializar(_datos.jugador.efectos);
```

Lo que **no** se guarda, a propósito, igual que el `hitstun`/`blockstun` de 04 · 30 §6: las
inmunidades temporales de `MotorEfectos` (§5.4). Cargar una partida en pleno frame de inmunidad
por aturdimiento no debería congelar esa protección para siempre.

### 5.13 El registro de daño: medir lo que de verdad pasa

Con el pipeline montado, la pregunta que importa deja de ser «¿cuánto hace este ataque?» y pasa
a ser «¿cuánto hizo DE VERDAD, con resistencias y armadura de por medio, en la última sala?».
Esto extiende `telemetria_registrar()` (13 · 01 §9.5), ya alimentado desde el paso 5 de §5.7:

```gml
// ---------------------------------------------------------------------------
// scr_registro_dano
// ---------------------------------------------------------------------------

/// @func dano_desglose_por_origen()
/// @desc Suma el daño NETO de todos los eventos "golpe" registrados, agrupado
///       por quién los dio. Sobre global.telemetria.eventos (13 · 01 §9.5).
/// @returns {Struct}  { "obj_jugador": 340, "obj_esqueleto": 55, … }
function dano_desglose_por_origen()
{
    var _totales = {};
    var _eventos = global.telemetria.eventos;

    for (var i = 0; i < array_length(_eventos); i++)
    {
        var _e = _eventos[i];
        if (_e.tipo != "golpe") continue;

        var _actual = variable_struct_exists(_totales, _e.origen) ? _totales[$ _e.origen] : 0;
        _totales[$ _e.origen] = _actual + _e.neto;
    }
    return _totales;
}

/// @func dano_dps_medido(_origen, _ventana_ms)
/// @desc DPS REAL de `_origen` en los últimos `_ventana_ms` — para compararlo
///       con el DPS de DISEÑO de tiempo_para_matar() (13 · 01 §9.4).
/// @param {String} _origen
/// @param {Real}   _ventana_ms
/// @returns {Real}
function dano_dps_medido(_origen, _ventana_ms)
{
    var _eventos = global.telemetria.eventos;
    var _ahora   = (get_timer() - global.telemetria.inicio) div 1000;
    var _suma    = 0;

    for (var i = array_length(_eventos) - 1; i >= 0; i--)
    {
        var _e = _eventos[i];
        if (_ahora - _e.ms > _ventana_ms) break;   // los eventos van en orden: cortar basta
        if (_e.tipo == "golpe" && _e.origen == _origen) _suma += _e.neto;
    }
    return _suma / (_ventana_ms / 1000);
}
```

```gml
/// obj_panel_dano · Create — junto al panel de balance de 13 · 01 §9.4
if (!debug_mode) { instance_destroy(); exit; }

dbg_view("Registro de daño", true);
dbg_section("DPS medido (ventana de 5 s)");
dps_jugador = 0;
dbg_watch(ref_create(self, "dps_jugador"), "obj_jugador");
dbg_text_separator("Compáralo con tiempo_para_matar() de 13 · 01 §9.4");

/// obj_panel_dano · Step
dps_jugador = dano_dps_medido("obj_jugador", 5000);
```

Con esto, «¿la sala 7 mata más que la 6?» (la pregunta que 13 · 01 §4.4 pide hacerte antes de
registrar nada) se contesta con datos: el DPS medido de cada enemigo, agrupado por sala, frente
al TTK de diseño de la hoja de cálculo.

---

## 6. Gestión del estado: lo que se añade a `EstadoCombate`

Todo lo nuevo de este documento sigue la misma regla que ya fija 04 · 30 §6 para el resto del
combate: **vive en el struct, no en variables sueltas de la instancia**, y se actualiza con un
único `tick()` por pieza, no con `alarm[N]` repartidas.

- **Al morir** (`fsm.set("muerto")`, 04 · 30 §6): llama a `combate.efectos.limpiar()`. Un
  cadáver envenenado que sigue restando vida a un `hp` que ya es 0 no hace daño real, pero sigue
  llamando a `on_tic()` para siempre si no lo limpias — un desperdicio silencioso, no un bug
  visible, que se nota en el profiler cuando hay cien cadáveres en la sala.
- **El escudo NO se limpia al morir**: no importa, la instancia va a destruirse. Si reciclas la
  instancia con *object pooling* (04 · 30 §8, `scr_pool.gml`), resetéalo igual que `ya_golpeados`:
  `combate.escudo.capacidad = combate.escudo.capacidad_max;`.
- **Orden de creación**: `combate.efectos = new MotorEfectos(combate)` necesita que `combate` YA
  exista. Créalo siempre después de `new EstadoCombate(...)`, nunca antes (§5.6 ya lo hace bien).
- **Qué NO se serializa** (§5.12): inmunidades temporales, `tic_restante` (se recalcula al
  cargar, para que el primer tic tras cargar no llegue a destiempo) y, como ya documentaba
  04 · 30 §6, todos los aturdimientos.

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Tick de efectos DESPUÉS del `exit` por `tiene_control()` | El veneno se detiene mientras el objetivo está aturdido | `combate.efectos.tick()` va ANTES del corte (§3) |
| Forzar `max(1, …)` sobre el daño YA mitigado por resistencia | Ningún enemigo puede ser inmune de verdad: un `0` se convierte en `1` | El mínimo de 1 sólo se aplica al daño BRUTO, antes de resistencias (§5.7) |
| Mezclar armadura plana y porcentual en el mismo enemigo | Nadie sabe cuál «manda»; el balance se vuelve impredecible | Elige una familia por proyecto (§1.3); documenta la decisión en el propio código |
| Política `APILAR` sin `pilas_max` | Un jugador con diez fuentes de veneno mata instantáneamente a cualquier cosa | Todo efecto con `APILAR` lleva un `pilas_max` explícito (§5.5) |
| Aturdimiento sin `inmunidad_frames` | Dos enemigos aturdidores encadenan un "stunlock" infinito: el jugador nunca recupera el control | `inmunidad_frames` tras expirar (§5.4), como el aguante de 04 · 30 §6 |
| `on_aplicar`/`on_quitar` fuera de un `with` | El callback usa `self`/`other` y apunta a la instancia equivocada | Pasa siempre `combate` explícito como parámetro (§5.4), nunca dependas de `self` implícito |
| Escudo que se rompe sin *feedback* | El jugador no entiende por qué de repente empieza a perder vida | Engancha sonido/flash al primer fotograma en que `escudo.roto` pasa a `true` (§5.3) |
| Guardar `tic_restante` tal cual | Al cargar, todos los efectos tiquean en el mismo fotograma exacto, o en 0 | Se recalcula a `_def.tic_frames` en `deserializar()` (§5.4), nunca se guarda |
| Curación sin bloqueo en un *soulslike* | El jugador se cura en pleno combo y el combate pierde tensión | `combate.bloqueo_curacion` tras cada golpe recibido (§5.9); en un JRPG por turnos, ponlo a 0 |
| Icono de estado sin contador de pilas | El jugador no sabe si el veneno está a punto de matarlo o acaba de aplicarse | `efectos_dibujar_fila()` dibuja el número en cuanto `pilas > 1` (§5.10) |
| Resistencia sumada en vez de multiplicada con dos tipos a la vez | Los números dejan de tener sentido con combinaciones (`fuego + hielo = 0`, ¿en vez de qué?) | Multiplica los factores, como el sistema de tipos de §1.2, nunca los sumes |
| Barra de jefe sin segmentos | El jugador no sabe si va a cambiar de fase pronto o le quedan diez minutos | `barra_jefe_dibujar()` añade los separadores sobre la barra ya existente (§5.11) |

---

## 8. Cómo escalarlo

Orden recomendado. Cada paso es jugable antes de pasar al siguiente — igual que 04 · 30 §8.

1. **Un solo tipo de daño (físico) y un solo enemigo con resistencia binaria** (0 o 1). Aquí es
   donde se prueba que `dano_resolver()` está bien enganchado en `recibir_golpe()`.
2. **Armadura plana** en dos o tres enemigos. Es la capa más fácil de leer para el jugador.
3. **Tabla de resistencias por tipo, cargada de datos** (§5.1) para el resto del bestiario. Aquí
   es donde el triángulo elemental empieza a generar decisiones de verdad (§1.2).
4. **El motor de efectos con UN solo efecto** (veneno). Verifica el apilado y la duración antes
   de añadir el resto: un solo efecto mal enganchado es más fácil de depurar que seis.
5. **El resto de efectos concretos + la fila de iconos** (§5.5, §5.10).
6. **Escudos**, si el juego los necesita. No son universales: muchos ARPG no los tienen.
7. **Armadura porcentual + penetración** cuando el juego tenga suficientes niveles de armadura
   para que la plana deje de escalar bien (§1.3).
8. **Barra de jefe segmentada** para el primer jefe con fases reales.
9. **El registro de daño y el DPS medido** (§5.13) cuando el balance empiece a doler y haga
   falta comparar la hoja de cálculo con lo que pasa de verdad en una sala.

**Cuando el sistema crezca:**

- **Resistencias por equipo, no sólo por enemigo.** Un anillo que da `resistencias.fuego += 0.3`
  es un modificador más sobre la misma tabla: súmalo al leer, no al guardar el dato base — el
  mismo patrón que `get_equip_bonus()` en `04 · 04 §5.0`.
- **Efectos con área**, en vez de sólo por golpe directo: una nube de veneno que aplica
  `efectos.aplicar("veneno", …)` a todo lo que pisa la zona, reutilizando `obj_hitbox` de
  04 · 30 §5.3 con un `refresco` alto en vez de crear un sistema aparte.
- **Resistencia que cambia con el estado**: un enemigo que se vuelve inmune al fuego mientras
  está congelado es sólo leer `combate.efectos.tiene("congelacion")` dentro de
  `resistencia_obtener()` antes de devolver el factor — sin tocar el motor.

---

## Ver también

- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md) —
  `EstadoCombate`, `recibir_golpe()` y la tabla de ataques que este documento amplía.
- [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — `hit_complete()`,
  `fx_floating_text()`, `apply_knockback()` y el resto de la sensación del golpe.
- [04 · 04 — RPG / Action RPG](./04%20-%20RPG%20_%20Action%20RPG.md) — `Stats`, `take_damage()`
  y `get_equip_bonus()`: el sistema de estadísticas al que engancha la armadura de este documento.
- [04 · 03 — Shoot 'em up (shmup)](./03%20-%20Shoot%20em%20up%20%28shmup%29.md) — el jefe con fases
  por `hp_threshold` que alimenta la barra segmentada de §5.11.
- [04 · 08 — Tower Defense](./08%20-%20Tower%20Defense.md) — la idea pendiente de resistencias
  por tipo (`§8`), con el mismo formato de tabla que §5.1 de este documento.
- [13 · 13 — Matemáticas aplicadas al juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
  `critico_tirar()` con piedad (*pity*), que se aplica ANTES de este pipeline (§1.1).
- [13 · 05 — UI y UX de juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md) —
  `barra_nueva/fijar/actualizar/dibujar`, que §5.11 envuelve sin reimplementar.
- [13 · 01 — Diseño de juego: core loop, mecánicas, balance y dificultad](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) —
  `telemetria_registrar()`, `tiempo_para_matar()` y el Debug Overlay que §5.13 extiende.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) —
  `guardar_partida()`/`cargar_partida()`, el patrón JSON que usa `resistencias_cargar()` (§5.1).
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — `global.a11y.reduce_motion`, que
  `barra_dibujar()` (reutilizada en §5.11) ya respeta.
- [12 · 06 — itch.io](../12%20-%20Utilidades%20e%20integraciones/06%20-%20itch.io%20-%20assets,%20herramientas%20y%20jams.md) —
  *Affliction — A Status System*, un motor de efectos de estado de terceros con iconos
  autogenerados, para quien prefiera no escribirse el suyo.

---

## 9. Fuentes

**Diseño y convenciones de fuera de GameMaker** (todas consultadas el 2026-09-06):

- **Type** (efectividad de tipos), Bulbapedia — la referencia mejor documentada del triángulo
  elemental como multiplicador de daño, con la regla exacta de combinación entre dos tipos —
  https://bulbapedia.bulbagarden.net/wiki/Type
- **Armor**, League of Legends Wiki — la fórmula porcentual de reducción de daño físico
  (`daño × 100/(100+armadura)`) y la idea de «vida efectiva» —
  https://wiki.leagueoflegends.com/en-us/Armor
- **Energy shielding**, Halopedia — los tres retardos de regeneración de escudo documentados por
  entrega (*Combat Evolved* 5 s, *Halo 2* 4,25 s, *Halo 3* 5 s) y la mecánica de ruptura por
  fuego sostenido — https://www.halopedia.org/Energy_shielding
- **Poison**, Old School RuneScape Wiki — el mecanismo de daño por tics con severidad
  decreciente, usado en §1.5 como referencia de un DoT que se apaga solo —
  https://oldschool.runescape.wiki/w/Poison
- ⚠️ La idea de que un sistema de tipos genera «decisiones significativas» (§1.2) sigue el
  criterio de *Designing Games*, Tynan Sylvester: no he abierto el libro en esta sesión, se cita
  de memoria como marco de diseño, no como fuente verificada de una cifra.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`; todos los
símbolos de GML de este documento comprobados con `_indice/buscar.py` contra el runtime
`2026.0.0.23`):

- `variable_struct_exists`, `array_push`/`array_delete`/`array_length` —
  familia *Variable Functions* del manual.
- `buffer_load`/`buffer_read`/`json_parse` — el patrón de lectura de JSON de
  [01 · 14 §8](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md), reutilizado
  tal cual en `resistencias_cargar()` (§5.1).
- `dbg_view`/`dbg_section`/`dbg_watch`/`ref_create` — familia *Debugging*, ya documentada en
  [13 · 01 §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md).

> ⚠️ **Lo que NO está verificado en este documento.** Todos los símbolos de GML existen en el
> runtime 2026.0.0.23 (comprobados uno a uno con `buscar.py`), pero el código **no se ha
> compilado en un proyecto real**: los sprites (`spr_icono_veneno`, `spr_icono_regeneracion`…)
> son marcadores de posición que tienes que crear, igual que en 04 · 30. Los **números** —2 de
> daño por pila de veneno, 15 de armadura, retardo de escudo de 90 fotogramas— son un punto de
> partida razonable, no medidas de ningún juego concreto: ajústalos con el panel de balance de
> [13 · 01 §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
> y con el registro de daño de §5.13.
