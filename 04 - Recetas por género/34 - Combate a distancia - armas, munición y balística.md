# 34 · Combate a distancia — armas, munición y balística

> **Dificultad:** media-alta · **Antes de esto:** el `WeaponDef` y el disparo básico de
> [04 · 02 §5.0-5.3](./02%20-%20Top-Down%20_%20Twin-Stick.md), y el pool de balas de
> [04 · 02 §5.5](./02%20-%20Top-Down%20_%20Twin-Stick.md).
> Este documento cierra lo que un twin-stick, un shooter en tercera persona o un tower
> defense necesitan y que `04/02` deja a medias: **cargador y reserva con recarga real**,
> **retroceso y dispersión que crece y se recupera**, **hitscan con penetración ordenada y
> caída de daño**, **asistencia de puntería** como ajuste de accesibilidad, y **cobertura**.
>
> **Qué NO cubre este documento** (y dónde está): los patrones de balas (anillo, abanico,
> espiral, *danmaku*) están en
> [04 · 03 §4.4 y §5.5](./03%20-%20Shoot%20em%20up%20%28shmup%29.md); el misil teledirigido con
> giro limitado y predicción está en
> [13 · 13 §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md);
> el *targeting* de torretas (First/Last/Strongest/Closest) está en
> [04 · 08 §4.4](./08%20-%20Tower%20Defense.md). ⚠️ **Los tipos de daño, las resistencias y los
> escudos** no son parte de este documento — es un sistema de datos aparte, hoy sin cubrir en
> la biblioteca (ver `_indice/auditorias/combate-enemigos.md`, propuesta P1): cuando exista,
> `falloff_min_mult` y el multiplicador de daño de este documento deben multiplicarse con su
> tabla de resistencias, no sustituirla.

---

## 1. Visión general

`04/02` te da un arma como *struct* (`WeaponDef`) y un contador de munición plano
(`ammo[$ nombre]`, -1 = infinita). Eso basta para un prototipo. En cuanto el juego pide que
recargar sea una decisión —¿recargo ahora, con el pasillo despejado, o espero?— o que un rifle
de francotirador se sienta distinto de una escopeta, el contador plano se queda corto. Este
documento añade la capa que falta **sin tocar el struct que ya tienes**: lo extiende.

**Lo que cubre, en una tabla:**

| Tema | Auditoría | Qué añade |
|---|---|---|
| Cargador, reserva y recarga (con recarga activa) | A9 | `WeaponAmmoState`: estados, cancelación, ventana de recarga activa |
| Retroceso y dispersión creciente (*bloom*) | A10 | Dispersión que crece al disparar y se recupera al soltar, más *kick* de cámara |
| Hitscan con penetración y caída de daño | A12 | `collision_line_list` (nativa, ordenada) resuelve de raíz el límite de `collision_line` |
| Asistencia de puntería | A2 | Corrección de ángulo por cono, con interruptor de accesibilidad |
| Cobertura | A13 | Parapetos, línea de tiro despejada, y el esqueleto de la IA que los usa |

**A quién le hace falta:** cualquier receta con combate a distancia — `04/02`
(top-down/twin-stick), `04/08` (torres con hitscan), un *cover shooter* en tercera persona,
o un *survival* con munición limitada (`04/09`).

**Lo que NO vas a encontrar aquí:** un motor de daño con tipos y resistencias, un sistema de
escudos, o una IA de decisión completa. Ese trabajo vive en otros documentos (ver arriba y
[Ver también](#ver-también)); aquí solo se **usa**, nunca se reimplementa.

---

## 2. Arquitectura recomendada

### 2.1 Dos structs, dos responsabilidades

`WeaponDef` (04/02 §5.0) es **dato compartido**: una pistola es la misma pistola para
cualquier portador. El estado de una recarga en curso, el cargador actual y la dispersión que
ha crecido por disparar sin soltar el gatillo son **por portador**: dos enemigos con el mismo
rifle no comparten cargador. De ahí el segundo struct:

```
WeaponDef            (04/02 §5.0 — AMPLIADO en §5.0 de este documento)
  · dato compartido: daño, cadencia, velocidad de bala, cargador, recarga,
    hitscan, alcance, penetración, caída de daño, dispersión mín/máx,
    retroceso, asistencia de puntería

WeaponAmmoState(_def)  (NUEVO — §5.1 de este documento)
  · estado por portador: cargador actual, si está recargando, cuánto queda,
    resultado de la recarga activa, dispersión ACTUAL (crece y se recupera)
  · uno por arma y por portador: objPlayer.ammo_state, objEnemyRanged.ammo_state…

PlayerStateTopDown.ammo   (04/02 §6 — sin tocar)
  · sigue guardando la RESERVA (las balas que no están en el cargador).
    WeaponAmmoState.actualizar() la consulta y la descuenta; no la duplica.
```

### 2.2 Qué debes tener ya

- El `WeaponDef` y `fire_weapon()` de `04/02 §5.0-5.3`, y el pool de balas de `04/02 §5.5`.
- `objSolid` como objeto de muro y `objEnemy` como objetivo — o sus equivalentes; cambia los
  nombres si tu proyecto usa otros.
- De `13/13`, sin redefinirlas — cópialas una vez a tu proyecto (por ejemplo a
  `scr_matematicas_combate`) y llama a la que necesites:
  `girar_hacia` (§3.2), `en_cono_vision` y `dot_product_normalised` (§2.4),
  `cortan_segmentos` (§6.5). Este documento las **usa**; `13/13` es donde están escritas y
  probadas.
- `global.a11y` de `04/27` — el struct de ajustes de accesibilidad donde vive el interruptor
  de asistencia de puntería.

### 2.3 Hitscan frente a proyectil: cuándo usar cada uno

`04/08 §4.5` ya resume la decisión para torres; aquí se aplica igual a un arma de jugador:

| | Proyectil (pool de `04/02 §5.5`) | Hitscan (`§5.4` de este documento) |
|---|---|---|
| Se puede esquivar | Sí — el jugador ve venir la bala | No — el impacto es instantáneo |
| Coste | Una instancia por bala, cientos por segundo | Una consulta por disparo, cero instancias persistentes |
| Encaja con | Escopetas, lanzacohetes, cualquier arma "lenta" | Rifles, pistolas, láseres, torretas rápidas |
| `WeaponDef.hitscan` | `false` (por defecto, como ya está en `04/02`) | `true` |

---

## 3. El bucle central de un disparo, con todo lo nuevo

```
┌─ Antes de apuntar ──────────────────────────────────────────────────┐
│ 1. Dirección en bruto: ratón o stick derecho (04/02 §5.2, sin cambios)│
│ 2. Asistencia de puntería (§4.4): corrige el ángulo hacia el mejor    │
│    objetivo dentro de un cono, como mucho unos pocos grados por frame│
└────────────────────────────────────────────────────────────────────┘
┌─ Al pulsar disparo ───────────────────────────────────────────────────┐
│ 3. ¿ammo_state.puede_disparar()? → cargador > 0 y no está recargando  │
│ 4. ¿weapon.hitscan?                                                    │
│    NO → ráfaga con weapon_angulos_con_dispersion() (usa la dispersión │
│         ACTUAL, no la fija: es el "bloom" de §4.2)                     │
│    SÍ → hitscan_resolver() (§4.3): muro más cercano limita el alcance,│
│         penetra objetivos ORDENADOS por distancia, aplica caída de    │
│         daño                                                           │
└────────────────────────────────────────────────────────────────────┘
┌─ Tras el disparo ─────────────────────────────────────────────────────┐
│ 5. ammo_state.consumir_disparo(): -1 bala del cargador, la dispersión │
│    actual sube un escalón                                              │
│ 6. Retroceso: empuje al portador + camera_shake (04/02 §5.7, reutilizado)│
└────────────────────────────────────────────────────────────────────┘
┌─ Cada Step, dispare o no ──────────────────────────────────────────────┐
│ 7. ammo_state.actualizar(reserva): recupera dispersión; si está        │
│    recargando, cuenta el temporizador y rellena desde la reserva al    │
│    terminar                                                             │
│ 8. HUD: cargador/reserva y barra de progreso de recarga (§5.2)         │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Cargador y reserva: la anatomía de una recarga

Una recarga real no es "espera 60 frames y listo". Tiene fases, y cada una es una decisión de
diseño:

| Fase | Qué pasa | Palanca de diseño |
|---|---|---|
| **Arranque** | El jugador pulsa recargar; si el cargador no está vacío, sigue disparando con lo que le queda hasta soltar el gatillo o decidir recargar | Permitir recargar con balas en el cargador, o exigir vaciarlo primero |
| **En curso** | El portador no puede disparar (o dispara más lento, según el arma); un contador cuenta hacia atrás | `reload_frames`: cuanto más larga, más presión táctica de "¿recargo ya?" |
| **Recarga activa** (opcional, *Gears of War*) | Una ventana de unos pocos frames dentro de la recarga: acertar el botón ahí completa la recarga al instante | Ventana estrecha = recompensa a la habilidad; ancha = casi gratis |
| **Cancelación** | Un evento (esquivar, cambiar de arma) interrumpe la recarga a medias | El cargador se queda con lo que tenía: **nunca** se pierde ni se rellena a medias |
| **Fin** | Se rellena el cargador desde la reserva, como mucho hasta `clip_size` | Si la reserva no llega para llenarlo, el cargador se queda a medias — no es un error |

El error más común es guardar "está recargando" como un booleano suelto y "cuánto queda" en
otro sin relacionarlos: se acaban desincronizando en cuanto hay cancelación. `WeaponAmmoState`
(§5.1) los junta en un solo struct con una única función `actualizar()` que se llama una vez
por Step.

### 4.2 Retroceso y dispersión creciente (*bloom*)

`04/02 §5.0` ya tiene `spread_deg`: una dispersión **fija**. Lo que falta es que crezca al
mantener el gatillo y se recupere al soltarlo — el patrón de práctica casi cualquier shooter
con armas automáticas.

```
dispersión
    │                    ╱‾‾‾‾‾ spread_max_deg (tope)
    │                 ╱‾
    │              ╱‾
    │           ╱‾
    │  ______╱‾                                    ╲______
    │ spread_min_deg (reposo)                              ╲______
    └────────────────────────────────────────────────────────────── tiempo
       disparando (crece _growth por bala)   soltado (recupera _recovery/frame)
```

Dos curvas, dos números: `spread_growth_deg` (cuánto sube cada disparo) y
`spread_recovery_deg` (cuánto baja cada frame sin disparar). Un SMG con `growth` alto y
`recovery` lento premia ráfagas cortas; un rifle con `growth` bajo perdona el fuego sostenido.

El retroceso **de cámara** es distinto de la dispersión: no cambia dónde va la bala, solo
cómo se *siente* el disparo. Reutiliza `camera_shake()` de `04/02 §5.7` — no hace falta un
sistema nuevo.

### 4.3 Hitscan: los tres límites de `collision_line`, resueltos

`13/13 §6.8` documenta los tres límites de `collision_line` y su alternativa "a mano"
(recorrer segmentos con `cortan_segmentos` y quedarse con la `u` menor). El mismo runtime
tiene una función hermana que resuelve el primero de raíz sin escribir ese bucle:
**`collision_line_list(x1, y1, x2, y2, obj, prec, notme, list, ordered)`** — verificada en el
manual oficial (es/en) y en el tutorial *Ultimate Guide To Collision Functions*
([fuente](#9-fuentes)). Con `ordered = true`, la lista de instancias en colisión llega
**ordenada por distancia desde el inicio de la línea** (el manual en inglés lo deja preciso;
⚠️ el espejo en español de esta misma página dice "desde el centro de la línea", que es una
traducción imprecisa del original — no toques `09 - Manual oficial/`: ese espejo es una copia
literal de la fuente y su corrección es tarea aparte de este documento).

Los tres límites de `13/13 §6.8`, y cómo quedan aquí:

| Límite (13/13 §6.8) | Resuelto con |
|---|---|
| Devuelve una instancia cualquiera, no la más cercana | `collision_line_list(..., ordered: true)`: la lista ya viene ordenada — sin recorrer nada a mano |
| Solo detecta instancias, no *tilemaps* | `collision_line_list` también acepta un *Tile Map Element ID* (`layer_tilemap_get_id()`) o un **array** mezclando objetos y *tilemaps* en una sola llamada |
| Con `prec = true` exige colisión precisa en el sprite | Sigue aplicando igual aquí: usa `false` (caja) salvo que el sprite del muro tenga colisión precisa activada en el editor |

Lo único que `collision_line_list` no te da gratis es el **punto exacto** de impacto en el
muro más cercano (solo te da la instancia). Para eso, una vez sabes CUÁL muro es el más
cercano, basta comprobar sus 4 aristas con `cortan_segmentos` (13/13 §6.5) — ya no hace falta
recorrer todos los muros de la sala, solo ese uno (§5.4).

La **penetración** (atravesar varios objetivos) sale del mismo mecanismo: pide la lista de
`objEnemy` ordenada hasta el punto de impacto en el muro (o el final del alcance si no hay
muro) y toma como mucho `pierce_max` elementos, aplicando la caída de daño según la distancia
de cada uno.

### 4.4 Asistencia de puntería, como ajuste de accesibilidad

Wikipedia recoge tres familias de técnicas bajo "*aim assist*"
([fuente](#9-fuentes), consultada 2026-09-06): **zoom/target snapping** (fija la mira sobre un
objetivo), ***slowdown*** (frena el movimiento de la mira al cruzar un objetivo) y
***magnetism*** (dobla la trayectoria hacia el objetivo). Este documento implementa la
variante de **corrección de ángulo**, más cercana al *magnetism*: no teletransporta la mira,
la dobla como mucho unos pocos grados por disparo hacia el objetivo mejor alineado dentro de
un cono — reutilizando `en_cono_vision` y `girar_hacia` de `13/13`, sin reescribirlas.

Es, ante todo, **un ajuste de accesibilidad**, no solo una comodidad para mando: para quien
tiene dificultad motriz fina, unos grados de corrección son la diferencia entre poder jugar o
no. Por eso vive como un interruptor más en `global.a11y` (`04/27`), no como un modo aparte:

```gml
// Extensión de global.a11y (04/27) — añade este campo junto a los demás del struct:
//   asistencia_punteria: false,   // corrección de ángulo hacia el objetivo alineado
```

Con el interruptor apagado, `aim_assist_corregir()` devuelve la dirección tal cual: el sistema
no penaliza a quien no lo quiere.

### 4.5 Cobertura: parapetos, línea de tiro y la IA que los usa

Un sistema de cobertura completo (*Kill.Switch*, 2003, es el primero acreditado con la
cobertura como mecánica central; *Gears of War*, 2006, la llevó al diseño de niveles entero —
[fuente](#9-fuentes), consultada 2026-09-06) tiene mucho más recorrido del que cabe aquí:
disparo ciego, cambio de cobertura a cobertura, cobertura alta frente a baja. Este documento
cubre el **núcleo mínimo** que pide la auditoría (A13): marcar parapetos, comprobar si la
línea de tiro está despejada, y el esqueleto de la IA que busca y usa un punto de cobertura.

- **Marcar**: un objeto `objCobertura` colocado en la room, igual que `objSolid` pero con
  significado táctico en vez de físico.
- **Línea de tiro**: la misma pregunta que ya resuelve `collision_line` — "¿hay algo entre
  el tirador y el objetivo?" — pero contra `objCobertura` **y** `objSolid` a la vez.
- **La IA que la usa** no se reimplementa aquí: el **movimiento** hacia el punto de cobertura
  es *Seek*/*Arrive* de `04/23 §1-2`, y **cuándo** buscar cobertura (¿vida baja? ¿bajo fuego
  directo?) es un nodo más del árbol o la utilidad de `04/31`. Lo que aporta este documento es
  la pieza que falta entre los dos: **dónde** está el punto de cobertura válido más cercano.

---

## 5. Código base

### 5.0 Extensión de `WeaponDef` con munición y balística

```gml
// ---------------------------------------------------------------------------
// Extensión de WeaponDef (04/02 §5.0) — añade estas líneas DENTRO del
// constructor, justo después de `knockback = 2;`. No es un struct nuevo:
// son los campos que le faltan al que ya tienes.
// ---------------------------------------------------------------------------

// --- Munición: cargador y recarga ------------------------------------------
clip_size     = 12;         // balas por cargador. -1 = sin cargador (comportamiento actual)
reload_frames = 60;         // duración total de la recarga, en frames
active_window = undefined;  // [inicio, fin] en frames desde que arrancó, o undefined = sin recarga activa

// --- Balística: hitscan y penetración ---------------------------------------
hitscan          = false;   // true → collision_line_list en vez de bala física
alcance_max      = 800;     // solo se usa si hitscan == true
pierce_max       = 1;       // nº de objetivos que atraviesa UN disparo hitscan
falloff_start    = 9999;    // px antes de los cuales el daño es el 100 %
falloff_end      = 9999;    // px a partir de los cuales el daño es el mínimo
falloff_min_mult = 1.0;     // multiplicador de daño al final de la caída (0..1)

// --- Retroceso y dispersión creciente (bloom) -------------------------------
spread_min_deg      = spread_deg;      // dispersión en reposo: hereda la que ya tenías
spread_max_deg      = spread_deg * 3;  // dispersión al mantener el gatillo
spread_growth_deg   = 1.2;             // crece esto por CADA disparo
spread_recovery_deg = 2.0;             // se recupera esto por CADA frame sin disparar
recoil_kick         = 2;               // magnitud del camera_shake al disparar (px)

// --- Asistencia de puntería ---------------------------------------------------
aim_assist_cone_deg           = 6;    // apertura del cono de corrección, en grados
aim_assist_range              = 260;  // alcance del cono, en píxeles
aim_assist_max_correction_deg = 4;    // grados que corrige COMO MUCHO por disparo
```

```gml
// ---------------------------------------------------------------------------
// Ejemplo: un rifle semiautomático hitscan con recarga activa, y una
// escopeta de proyectiles sin ninguna de las dos cosas (para comparar).
// ---------------------------------------------------------------------------
global.weapons.rifle.hitscan          = true;
global.weapons.rifle.alcance_max      = 900;
global.weapons.rifle.pierce_max       = 2;         // atraviesa hasta 2 enemigos en línea
global.weapons.rifle.falloff_start    = 300;
global.weapons.rifle.falloff_end      = 700;
global.weapons.rifle.falloff_min_mult = 0.4;
global.weapons.rifle.clip_size        = 20;
global.weapons.rifle.reload_frames    = 90;
global.weapons.rifle.active_window    = [55, 65];  // 10 frames de recarga activa

global.weapons.shotgun.clip_size     = 6;
global.weapons.shotgun.reload_frames = 120;        // recarga larga: es la contrapartida del daño
// La escopeta se queda hitscan == false: usa el pool de balas de 04/02 §5.5 sin cambios.
```

### 5.1 `WeaponAmmoState` — cargador, recarga y recarga activa

```gml
// ---------------------------------------------------------------------------
// scr_weapon_ammo_state
// ---------------------------------------------------------------------------

/// @func WeaponAmmoState(_def)
/// @desc Estado de munición y recarga de UN arma en manos de UN portador.
///       WeaponDef (04/02 §5.0, extendido en §5.0 de este documento) es dato
///       compartido; esto es lo que cambia disparo a disparo. La RESERVA
///       sigue viviendo en PlayerStateTopDown.ammo (04/02 §6): esta función
///       la consulta y la descuenta, nunca la duplica.
function WeaponAmmoState(_def) constructor
{
    def           = _def;
    clip          = _def.clip_size;
    reloading     = false;
    reload_timer  = 0;           // cuenta ATRÁS desde def.reload_frames
    active_result = "ninguno";   // "ninguno" | "perfecto" | "fallado"
    spread_actual = _def.spread_min_deg;

    /// @desc ¿Puede disparar AHORA MISMO?
    puede_disparar = function()
    {
        return !reloading && (clip > 0 || def.clip_size < 0);   // clip_size < 0 = sin cargador
    };

    /// @desc Gasta una bala del cargador y sube un escalón la dispersión.
    ///       Llamar tras CADA disparo válido (una vez, no una vez por bala
    ///       de la ráfaga: una escopeta gasta 1 del cargador, no 6).
    consumir_disparo = function()
    {
        if (def.clip_size >= 0) clip = max(0, clip - 1);
        spread_actual = min(def.spread_max_deg, spread_actual + def.spread_growth_deg);
    };

    /// @desc Relaja la dispersión hacia el reposo. Llamar UNA vez por Step,
    ///       se dispare o no (lo hace actualizar(), más abajo).
    recuperar_dispersion = function()
    {
        spread_actual = max(def.spread_min_deg, spread_actual - def.spread_recovery_deg);
    };

    /// @desc Arranca la recarga si hace falta y hay reserva.
    /// @param {Real} _reserva_disponible  Balas en la reserva (fuera del cargador).
    /// @return {Bool}  false si no hacía falta recargar o no hay reserva.
    iniciar_recarga = function(_reserva_disponible)
    {
        if (reloading)                    return false;
        if (clip >= def.clip_size)        return false;   // ya está lleno
        if (_reserva_disponible <= 0)     return false;

        reloading     = true;
        reload_timer  = def.reload_frames;
        active_result = "ninguno";
        return true;
    };

    /// @desc Cancela la recarga a medias (esquivar, cambiar de arma…). El
    ///       cargador se queda con lo que tenía: no se pierde ni se rellena.
    cancelar_recarga = function()
    {
        if (!reloading) return;
        reloading    = false;
        reload_timer = 0;
    };

    /// @desc Recarga ACTIVA (Gears of War): si se pulsa dentro de
    ///       def.active_window, la recarga se completa ya y sin penalización.
    ///       Si def.active_window es undefined, esta función no hace nada:
    ///       el arma simplemente no tiene recarga activa.
    intentar_recarga_activa = function()
    {
        if (!reloading || is_undefined(def.active_window)) return;

        var _transcurrido = def.reload_frames - reload_timer;
        if (_transcurrido >= def.active_window[0] && _transcurrido <= def.active_window[1])
        {
            active_result = "perfecto";
            reload_timer  = 1;    // el próximo actualizar() la cierra ya
        }
        else if (active_result == "ninguno")
        {
            active_result = "fallado";   // el arma puede penalizar esto en su HUD (§5.2)
        }
    };

    /// @desc Llamar UNA vez por Step. Recupera dispersión siempre; si está
    ///       recargando, cuenta el temporizador y rellena desde la reserva
    ///       al terminar.
    /// @param {Real} _reserva_disponible  Balas en la reserva AHORA MISMO.
    /// @return {Real}  Cuántas balas hay que restar de la reserva (0 si la
    ///                 recarga no ha terminado este Step).
    actualizar = function(_reserva_disponible)
    {
        recuperar_dispersion();

        if (!reloading) return 0;

        reload_timer--;
        if (reload_timer > 0) return 0;

        var _faltan  = def.clip_size - clip;
        var _a_tomar = min(_faltan, _reserva_disponible);
        clip         += _a_tomar;
        reloading     = false;
        active_result = "ninguno";
        return _a_tomar;
    };
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create (añadir junto a `weapon = global.weapons.pistol;` de
// 04/02 §5.1)
// ---------------------------------------------------------------------------
ammo_state = new WeaponAmmoState(weapon);
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step (añadir junto a los temporizadores del 04/02 §5.2)
// ---------------------------------------------------------------------------
var _reserva = global.player_state.ammo[$ weapon.nombre];
var _tomadas = ammo_state.actualizar(_reserva);
if (_tomadas > 0)
{
    global.player_state.ammo[$ weapon.nombre] -= _tomadas;
}

if (keyboard_check_pressed(ord("R")))
{
    ammo_state.iniciar_recarga(global.player_state.ammo[$ weapon.nombre]);
}

// Solo tiene efecto si weapon.active_window no es undefined (ver §5.1)
if (keyboard_check_pressed(vk_space))
{
    ammo_state.intentar_recarga_activa();
}
```

> ⚠️ Al **cambiar de arma**, sustituye `ammo_state` por uno nuevo:
> `ammo_state = new WeaponAmmoState(weapon);`. Si no lo haces, el cargador y la dispersión del
> arma anterior se cuelan en la nueva. El cambio de arma en sí (input, HUD) no está cubierto
> aquí ni en `04/02` (la auditoría lo marca como nota menor de A14): es hueco conocido, no un
> olvido de este documento.

### 5.2 HUD de munición y recarga

```gml
// ---------------------------------------------------------------------------
// objHudMunicion — Draw GUI
// ---------------------------------------------------------------------------
var _arma    = objPlayer.weapon;
var _estado  = objPlayer.ammo_state;
var _reserva = global.player_state.ammo[$ _arma.nombre];

var _texto_cargador = (_arma.clip_size < 0)
    ? "∞"
    : string(_estado.clip) + " / " + ((_reserva == -1) ? "∞" : string(_reserva));

draw_set_halign(fa_right);
draw_set_valign(fa_bottom);
draw_set_color(c_white);
draw_text(display_get_gui_width() - 24, display_get_gui_height() - 24, _texto_cargador);

if (_estado.reloading)
{
    var _bx1 = display_get_gui_width() - 140;
    var _bx2 = display_get_gui_width() - 24;
    var _by1 = display_get_gui_height() - 50;
    var _by2 = display_get_gui_height() - 40;

    var _progreso = 1 - (_estado.reload_timer / _arma.reload_frames);
    draw_healthbar(_bx1, _by1, _bx2, _by2, _progreso * 100,
                   c_black, c_yellow, c_lime, 0, false, true);

    // Marca de la ventana de recarga activa sobre la misma barra, si existe
    if (!is_undefined(_arma.active_window))
    {
        var _ancho = _bx2 - _bx1;
        var _mx1   = _bx1 + (_arma.active_window[0] / _arma.reload_frames) * _ancho;
        var _mx2   = _bx1 + (_arma.active_window[1] / _arma.reload_frames) * _ancho;

        draw_set_color(_estado.active_result == "perfecto" ? c_lime : c_white);
        draw_rectangle(_mx1, _by1, _mx2, _by2, true);
    }
}

draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_set_color(c_white);
```

### 5.3 Disparo con retroceso, dispersión y asistencia de puntería

```gml
// ---------------------------------------------------------------------------
// scr_weapon_spread
// ---------------------------------------------------------------------------

/// @func weapon_angulos_con_dispersion(_arma, _base_dir, _dispersion_actual)
/// @desc Igual que weapon.get_angles() (04/02 §5.0), pero con la dispersión
///       ACTUAL (crece disparo a disparo, se recupera al soltar) en vez de
///       la fija spread_deg. No sustituye a get_angles(): quien no quiera
///       bloom sigue usando el de siempre.
function weapon_angulos_con_dispersion(_arma, _base_dir, _dispersion_actual)
{
    var _out  = [];
    var _half = _dispersion_actual * 0.5;

    if (_arma.bullets_per_shot <= 1)
    {
        array_push(_out, _base_dir + random_range(-_half, _half));
        return _out;
    }

    var _step = _dispersion_actual / (_arma.bullets_per_shot - 1);
    for (var _i = 0; _i < _arma.bullets_per_shot; _i++)
    {
        array_push(_out, _base_dir - _half + (_step * _i));
    }
    return _out;
}
```

```gml
// ---------------------------------------------------------------------------
// scr_player_combat_avanzado
// ---------------------------------------------------------------------------

/// @func disparar_arma_avanzado(_dir_cruda)
/// @desc Sustituye a fire_weapon() (04/02 §5.3) cuando el arma tiene
///       cargador, hitscan o asistencia de puntería. Bifurca a
///       hitscan_disparar() (§5.4) o al pool de balas de 04/02 §5.5 según
///       weapon.hitscan. Llamar desde objPlayer — Step en vez de
///       fire_weapon(aim_dir).
/// @return {Bool}  false si no se pudo disparar (sin munición, recargando).
function disparar_arma_avanzado(_dir_cruda)
{
    if (!ammo_state.puede_disparar()) return false;

    var _dir = aim_assist_corregir(_dir_cruda, x, y, objEnemy, weapon);

    var _muzzle_x = x + lengthdir_x(14, _dir);
    var _muzzle_y = y + lengthdir_y(14, _dir);

    if (weapon.hitscan)
    {
        hitscan_disparar(weapon, _muzzle_x, _muzzle_y, _dir);
    }
    else
    {
        var _angles = weapon_angulos_con_dispersion(weapon, _dir, ammo_state.spread_actual);
        var _n      = array_length(_angles);

        for (var _i = 0; _i < _n; _i++)
        {
            var _b = bullet_pool_get();   // 04/02 §5.5
            if (_b == noone) break;

            with (_b)
            {
                x            = _muzzle_x;
                y            = _muzzle_y;
                direction    = _angles[_i];
                speed        = other.weapon.bullet_speed;
                damage       = other.weapon.damage;
                owner        = other.id;
                sprite_index = other.weapon.sprite_bullet;
                active       = true;
                life_frames  = 180;
            }
        }
    }

    ammo_state.consumir_disparo();

    // Retroceso: empuje al portador + camera_shake, reutilizando 04/02 §5.7
    vel_x -= lengthdir_x(weapon.recoil_kick, _dir);
    vel_y -= lengthdir_y(weapon.recoil_kick, _dir);
    objCamera.camera_shake(weapon.recoil_kick, 6);

    return true;
}
```

### 5.4 Arma hitscan: penetración ordenada y caída de daño

```gml
// ---------------------------------------------------------------------------
// scr_hitscan
// ---------------------------------------------------------------------------

/// @func hitscan_punto_impacto_en_muro(_x1, _y1, _x2, _y2, _muro)
/// @desc Dado que _muro YA es el más cercano (por collision_line_list
///       ordenada), calcula el punto EXACTO donde el rayo entra en su bbox,
///       recorriendo sus 4 aristas con cortan_segmentos (13/13 §6.5). Al ser
///       una sola instancia, esto no repite el barrido de todos los muros
///       que 13/13 §6.8 necesita cuando no se conoce cuál es el más cercano.
/// @return {Struct} { x, y, u }
function hitscan_punto_impacto_en_muro(_x1, _y1, _x2, _y2, _muro)
{
    var _mejor_u   = 2;                              // fuera de rango: cualquier corte real es menor
    var _resultado = { x: _x2, y: _y2, u: 1 };        // por si ninguna arista corta (caso raro)

    var _aristas = [
        [_muro.bbox_left,  _muro.bbox_top,    _muro.bbox_right, _muro.bbox_top],
        [_muro.bbox_right, _muro.bbox_top,    _muro.bbox_right, _muro.bbox_bottom],
        [_muro.bbox_right, _muro.bbox_bottom, _muro.bbox_left,  _muro.bbox_bottom],
        [_muro.bbox_left,  _muro.bbox_bottom, _muro.bbox_left,  _muro.bbox_top]
    ];

    for (var _i = 0; _i < 4; _i++)
    {
        var _a = _aristas[_i];
        var _c = cortan_segmentos(_x1, _y1, _x2, _y2, _a[0], _a[1], _a[2], _a[3]);
        if (_c != undefined && _c.u < _mejor_u) { _mejor_u = _c.u; _resultado = _c; }
    }
    return _resultado;
}

/// @func hitscan_caida_por_distancia(_distancia, _def)
/// @desc Multiplicador de daño según la distancia: completo antes de
///       falloff_start, el mínimo después de falloff_end, una recta en medio.
function hitscan_caida_por_distancia(_distancia, _def)
{
    if (_distancia <= _def.falloff_start) return 1.0;
    if (_distancia >= _def.falloff_end)   return _def.falloff_min_mult;

    var _t = (_distancia - _def.falloff_start) / (_def.falloff_end - _def.falloff_start);
    return lerp(1.0, _def.falloff_min_mult, _t);
}

/// @func hitscan_resolver(_x, _y, _dir, _def, _obj_objetivo, _obj_muro)
/// @desc Resuelve un disparo hitscan completo:
///       1) el muro más cercano limita el alcance real (collision_line_list
///          ordenada + el punto exacto en SU bbox, arriba);
///       2) penetra hasta _def.pierce_max objetivos, en orden de distancia
///          (de nuevo collision_line_list con ordered = true: así se resuelve
///          el límite de collision_line de 13/13 §6.8 —"devuelve una
///          instancia cualquiera, no la más cercana"— sin recorrer nada);
///       3) calcula la caída de daño de cada impacto.
/// @return {Struct} { x_final, y_final, impactos: [{inst, distancia, multiplicador}] }
function hitscan_resolver(_x, _y, _dir, _def, _obj_objetivo, _obj_muro)
{
    var _x2 = _x + lengthdir_x(_def.alcance_max, _dir);
    var _y2 = _y + lengthdir_y(_def.alcance_max, _dir);

    // --- 1) Muro más cercano: limita hasta dónde puede llegar el disparo ---
    var _lista_muros = ds_list_create();
    var _n_muros = collision_line_list(_x, _y, _x2, _y2, _obj_muro, false, true,
                                        _lista_muros, true);   // ordered = true

    var _x_final = _x2, _y_final = _y2;
    if (_n_muros > 0)
    {
        var _impacto = hitscan_punto_impacto_en_muro(_x, _y, _x2, _y2, _lista_muros[| 0]);
        _x_final = _impacto.x;
        _y_final = _impacto.y;
    }
    ds_list_destroy(_lista_muros);

    // --- 2) Objetivos entre el origen y el muro (o el final del alcance) ---
    var _lista_obj = ds_list_create();
    var _n_obj = collision_line_list(_x, _y, _x_final, _y_final, _obj_objetivo, false, true,
                                      _lista_obj, true);       // ordered = true

    var _impactos = [];
    var _tope     = min(_n_obj, _def.pierce_max);
    for (var _i = 0; _i < _tope; _i++)
    {
        var _obj = _lista_obj[| _i];
        var _d   = point_distance(_x, _y, _obj.x, _obj.y);
        array_push(_impactos, {
            inst: _obj,
            distancia: _d,
            multiplicador: hitscan_caida_por_distancia(_d, _def)
        });
    }
    ds_list_destroy(_lista_obj);

    return { x_final: _x_final, y_final: _y_final, impactos: _impactos };
}

/// @func hitscan_disparar(_arma, _x, _y, _dir)
/// @desc Aplica daño a cada impacto de hitscan_resolver() y lanza el trazador
///       y el impacto en el muro. Llamar desde disparar_arma_avanzado() (§5.3)
///       cuando weapon.hitscan == true.
function hitscan_disparar(_arma, _x, _y, _dir)
{
    var _res = hitscan_resolver(_x, _y, _dir, _arma, objEnemy, objSolid);
    var _n   = array_length(_res.impactos);

    for (var _i = 0; _i < _n; _i++)
    {
        var _imp = _res.impactos[_i];
        var _dano = _arma.damage * _imp.multiplicador;
        with (_imp.inst)
        {
            take_damage(_dano, _x, _y);
        }
    }

    // Impacto visual en el muro solo si el rayo terminó en un muro, no en el
    // final del alcance al aire.
    if (point_distance(_res.x_final, _res.y_final, _x + lengthdir_x(_arma.alcance_max, _dir),
                                                    _y + lengthdir_y(_arma.alcance_max, _dir)) > 1)
    {
        with (instance_create_layer(_res.x_final, _res.y_final, "Effects", objImpact))
        {
            image_angle = _dir + 180;
        }
    }

    trazador_crear(_x, _y, _res.x_final, _res.y_final);
}

/// @func trazador_crear(_x1, _y1, _x2, _y2)
/// @desc Crea el trazador visual de un disparo hitscan: una línea que se
///       desvanece en pocos frames. objTracer: Create solo guarda los 5
///       campos de abajo; Step cuenta `vida`; Destroy no hace falta.
function trazador_crear(_x1, _y1, _x2, _y2)
{
    with (instance_create_layer(_x1, _y1, "Effects", objTracer))
    {
        tx1  = _x1;
        ty1  = _y1;
        tx2  = _x2;
        ty2  = _y2;
        vida = 6;
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objTracer — Step
// ---------------------------------------------------------------------------
vida--;
if (vida <= 0) instance_destroy();

// ---------------------------------------------------------------------------
// objTracer — Draw
// ---------------------------------------------------------------------------
draw_set_alpha(vida / 6);
draw_set_color(c_yellow);
draw_line_width(tx1, ty1, tx2, ty2, 2);
draw_set_alpha(1);
draw_set_color(c_white);
```

> 💡 **Tus muros son un *tile layer*, no `objSolid`?** Sustituye `_obj_muro` por
> `layer_tilemap_get_id("Muros")` en la llamada a `hitscan_resolver()` — `collision_line_list`
> acepta un *Tile Map Element ID* igual que acepta un objeto (manual oficial, verificado
> arriba en §4.3). El resto de la función no cambia: sigue devolviendo instancias en la lista,
> salvo que ahora la lista puede contener el id de la propia *tilemap* en vez de una instancia,
> así que `hitscan_punto_impacto_en_muro()` dejaría de aplicar tal cual (usa `bbox_*` de una
> instancia) — para *tilemaps* usa en su lugar `tilemap_get_at_pixel()` a pasos cortos a lo
> largo del rayo, como ya apunta `13/13 §6.8`. ⚠️ No verificado en código real esta sesión.

### 5.5 Asistencia de puntería

```gml
// ---------------------------------------------------------------------------
// scr_aim_assist
// ---------------------------------------------------------------------------

/// @func aim_assist_mejor_objetivo(_x, _y, _dir_cruda, _obj_objetivo, _arma)
/// @desc Busca, dentro del cono de asistencia del arma alrededor de la
///       dirección de apuntado en bruto, el objetivo más alineado. Reutiliza
///       en_cono_vision y dot_product_normalised de 13/13 §2.4, sin
///       redefinirlas.
/// @return {Id.Instance}  El mejor candidato, o noone si ninguno cae en el cono.
function aim_assist_mejor_objetivo(_x, _y, _dir_cruda, _obj_objetivo, _arma)
{
    var _mejor     = noone;
    var _mejor_cos = -1;   // cuanto más alto (hasta 1), más alineado con _dir_cruda

    with (_obj_objetivo)
    {
        if (!en_cono_vision(_x, _y, _dir_cruda, _arma.aim_assist_cone_deg,
                             _arma.aim_assist_range, x, y))
        {
            continue;
        }

        var _fx  = lengthdir_x(1, _dir_cruda);
        var _fy  = lengthdir_y(1, _dir_cruda);
        var _cos = dot_product_normalised(_fx, _fy, x - _x, y - _y);

        if (_cos > _mejor_cos)
        {
            _mejor_cos = _cos;
            _mejor     = id;
        }
    }

    return _mejor;
}

/// @func aim_assist_corregir(_dir_cruda, _x, _y, _obj_objetivo, _arma)
/// @desc Dobla la dirección de apuntado, como mucho
///       _arma.aim_assist_max_correction_deg grados, hacia el objetivo mejor
///       alineado dentro del cono. Respeta global.a11y.asistencia_punteria
///       (04/27): si está desactivada, devuelve _dir_cruda sin tocar.
function aim_assist_corregir(_dir_cruda, _x, _y, _obj_objetivo, _arma)
{
    if (!global.a11y.asistencia_punteria) return _dir_cruda;

    var _objetivo = aim_assist_mejor_objetivo(_x, _y, _dir_cruda, _obj_objetivo, _arma);
    if (_objetivo == noone) return _dir_cruda;

    var _dir_ideal = point_direction(_x, _y, _objetivo.x, _objetivo.y);
    return girar_hacia(_dir_cruda, _dir_ideal, _arma.aim_assist_max_correction_deg);
}
```

### 5.6 Cobertura: marcar parapetos y comprobar línea de tiro

```gml
// ---------------------------------------------------------------------------
// objCobertura — Create
// ---------------------------------------------------------------------------
// Un objeto estático, colocado a mano en la room (o generado junto a la
// geometría del nivel). No necesita más estado que su posición y su bbox:
// la lógica vive toda en las funciones de abajo.
```

```gml
// ---------------------------------------------------------------------------
// scr_cobertura
// ---------------------------------------------------------------------------

/// @func cobertura_libre_de_impacto(_ox, _oy, _tx, _ty)
/// @desc ¿Hay línea de tiro despejada entre origen y objetivo? false si un
///       parapeto (objCobertura) o un muro (objSolid) la corta. La misma
///       pregunta que resuelve un disparo hitscan, pero sin resolver el
///       disparo: solo el booleano.
function cobertura_libre_de_impacto(_ox, _oy, _tx, _ty)
{
    return (collision_line(_ox, _oy, _tx, _ty, objCobertura, false, false) == noone)
        && (collision_line(_ox, _oy, _tx, _ty, objSolid,     false, false) == noone);
}

/// @func cobertura_buscar_punto(_x, _y, _amenaza_x, _amenaza_y, _alcance)
/// @desc Busca, entre los objCobertura a menos de _alcance, el más cercano
///       cuyo punto de resguardo (al lado opuesto a la amenaza) rompe la
///       línea de tiro desde la amenaza. No mueve nada: solo devuelve DÓNDE
///       ir. Moverse hasta ahí es Seek/Arrive de 04/23 §1-2.
/// @return {Struct|Undefined}  { x, y, cobertura } o undefined si no hay ninguna válida.
function cobertura_buscar_punto(_x, _y, _amenaza_x, _amenaza_y, _alcance)
{
    var _mejor_dist = _alcance;
    var _mejor      = undefined;

    with (objCobertura)
    {
        var _d = point_distance(_x, _y, x, y);
        if (_d > _mejor_dist) continue;

        // El punto de resguardo está detrás del parapeto, visto desde la amenaza.
        var _dir_resguardo = point_direction(_amenaza_x, _amenaza_y, x, y);
        var _px = x + lengthdir_x(12, _dir_resguardo);
        var _py = y + lengthdir_y(12, _dir_resguardo);

        if (!cobertura_libre_de_impacto(_px, _py, _amenaza_x, _amenaza_y))
        {
            _mejor_dist = _d;
            _mejor      = { x: _px, y: _py, cobertura: id };
        }
    }

    return _mejor;
}
```

### 5.7 IA que usa cobertura — el esqueleto mínimo

```gml
// ---------------------------------------------------------------------------
// objEnemyCobertura — Create
// ---------------------------------------------------------------------------
estado_cobertura = "buscando";   // "buscando" | "yendo" | "agachado" | "asomando"
objetivo_x = x;
objetivo_y = y;

// ---------------------------------------------------------------------------
// objEnemyCobertura — Step
// ---------------------------------------------------------------------------
// El QUÉ mover (steering) es 04/23 §1-2; el CUÁNDO buscar cobertura frente a
// avanzar es un nodo más del árbol o la utilidad de 04/31. Aquí solo el
// esqueleto de estados que conecta ambos con cobertura_buscar_punto().
switch (estado_cobertura)
{
    case "buscando":
        var _punto = cobertura_buscar_punto(x, y, objPlayer.x, objPlayer.y, 300);
        if (_punto != undefined)
        {
            objetivo_x = _punto.x;
            objetivo_y = _punto.y;
            estado_cobertura = "yendo";
        }
        break;

    case "yendo":
        // mover hacia (objetivo_x, objetivo_y) con Seek/Arrive — 04/23 §1-2
        if (point_distance(x, y, objetivo_x, objetivo_y) < 4)
        {
            estado_cobertura = "agachado";
            alarm[0] = 60 + irandom(60);   // tiempo agachado antes de asomar
        }
        break;

    case "agachado":
        // esperando alarm[0]; sin línea de tiro: invulnerable a hitscan del jugador
        break;

    case "asomando":
        if (cobertura_libre_de_impacto(x, y, objPlayer.x, objPlayer.y))
        {
            disparar_arma_avanzado(point_direction(x, y, objPlayer.x, objPlayer.y));
        }
        alarm[1] = 30;   // vuelve a agachado tras un tramo corto asomado
        break;
}
```

```gml
// ---------------------------------------------------------------------------
// objEnemyCobertura — Alarm 0 (fin del tiempo agachado → asoma a disparar)
// ---------------------------------------------------------------------------
estado_cobertura = "asomando";
```

```gml
// ---------------------------------------------------------------------------
// objEnemyCobertura — Alarm 1 (fin del tiempo asomando → vuelve a agachado)
// ---------------------------------------------------------------------------
estado_cobertura = "agachado";
alarm[0] = 90 + irandom(60);
```

---

## 6. Checklist

- [ ] `WeaponDef` extendido (§5.0): cada arma decide `hitscan`, `clip_size`,
      `pierce_max`, `falloff_*` y las curvas de dispersión — no hay un valor global
      compartido por todas las armas.
- [ ] `WeaponAmmoState` es **por portador**, no por arma compartida: al cambiar de arma
      se crea uno nuevo (§5.1, nota final).
- [ ] La cancelación de recarga deja el cargador tal cual estaba — nunca lo vacía ni lo
      rellena a medias.
- [ ] La dispersión se recupera **todos** los Steps, no solo cuando se dispara
      (`actualizar()` llama a `recuperar_dispersion()` siempre).
- [ ] El hitscan usa `collision_line_list` con `ordered = true`, no `collision_line` a
      secas — si no, la penetración golpea objetivos en el orden equivocado.
- [ ] La caída de daño se calcula por **impacto**, no una vez por disparo: dos enemigos a
      distinta distancia en la misma penetración reciben multiplicadores distintos.
- [ ] La asistencia de puntería comprueba `global.a11y.asistencia_punteria` antes de
      corregir nada, y el interruptor existe en las Opciones (04/27 + 04/25).
- [ ] `cobertura_libre_de_impacto()` comprueba **tanto** `objCobertura` **como**
      `objSolid`: una cobertura no sustituye a un muro real.
- [ ] Un enemigo `agachado` no dispara ni puede ser alcanzado por hitscan — si tu IA lo deja
      disparar desde ese estado, la cobertura no está haciendo nada.

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Un solo `WeaponAmmoState` compartido entre jugador y enemigos | Un enemigo recarga y el jugador también, sin haber disparado | Uno por portador, nunca uno global |
| Cancelar la recarga vaciando el cargador | El jugador pierde balas que ya tenía por esquivar a tiempo | `cancelar_recarga()` solo para el temporizador, no toca `clip` |
| `spread_actual` solo se recupera si `!disparando` en vez de siempre | La dispersión se queda "pegada" un frame después de soltar el gatillo | Llamar `recuperar_dispersion()` desde `actualizar()`, incondicional |
| Usar `collision_line` a secas para hitscan con varios objetivos | El primer enemigo golpeado depende del orden de creación, no de la distancia | `collision_line_list(..., ordered: true)` |
| Aplicar la caída de daño con la distancia AL MURO, no al objetivo | Todos los impactos de una penetración reciben el mismo multiplicador | `point_distance(origen, objetivo)` por cada impacto, no una vez |
| Asistencia de puntería sin comprobar el interruptor de accesibilidad | El jugador que la desactivó en Opciones la sigue notando | `aim_assist_corregir()` devuelve `_dir_cruda` sin tocar si el ajuste está apagado |
| Cobertura que solo comprueba `objCobertura` | Un enemigo "a cubierto" detrás de un parapeto sigue siendo alcanzable a través de la pared de al lado | Comprobar también `objSolid` en la misma línea de tiro |
| Punto de resguardo calculado desde el propio buscador, no desde la amenaza | El enemigo se cubre del lado equivocado del parapeto | `point_direction(_amenaza_x, _amenaza_y, x, y)`, no al revés |

---

## 8. Cómo escalarlo

1. **Multiplicador de resistencias en la caída de daño** — cuando exista el sistema de tipos
   de daño (`_indice/auditorias/combate-enemigos.md`, propuesta P1), `hitscan_disparar()`
   multiplica `_dano` por la resistencia del objetivo, no solo por `_imp.multiplicador`.
2. **Cobertura alta frente a baja** — un campo `agachado_visible` en `objCobertura`: la
   cobertura baja permite disparar por encima sin "asomar", solo con más dispersión.
3. **Disparo ciego** — disparar desde `agachado` con `aim_assist_max_correction_deg` mucho
   más generoso y precisión reducida: el clásico *blind fire* de los *cover shooters*.
4. **Recoil pattern aprendible** — en vez de `random_range(-_half, _half)` en
   `weapon_angulos_con_dispersion()`, una secuencia FIJA de desplazamientos por disparo (un
   array de offsets), como el patrón de recoil de un *arena shooter*: se puede memorizar y
   contrarrestar, a diferencia del `random_range` puro.
5. **`collision_line_list` con array mixto** — un único disparo que compruebe `objSolid`,
   `objCobertura` y una *tilemap* de terreno destructible a la vez, pasando
   `[objSolid, objCobertura, layer_tilemap_get_id("Destructible")]` como `obj` (el manual
   oficial confirma el array; no lo he probado en código real esta sesión).
6. **HUD de asistencia de puntería visible** — un indicador sutil (el reticle se tensa hacia
   el objetivo) en vez de una corrección invisible: ayuda a quien la usa a entender por qué
   el disparo "se ha ido solo" un poco.

**Cuándo pasar a otra receta:** cuando el arma decide todo esto por datos y ya no por `if`s
sueltos en el jugador, estás listo para que un enemigo dispare con el mismo
`disparar_arma_avanzado()` que el jugador — es la misma función, solo cambia quién la llama.

---

## Ver también

- [04 · 02 — Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) — el `WeaponDef`
  y el disparo base que este documento extiende (§5.0-5.3, §5.5, §6).
- [04 · 03 — Shoot 'em up (shmup)](./03%20-%20Shoot%20em%20up%20%28shmup%29.md) — patrones de
  balas (anillo, abanico, espiral) y el pool de balas enemigas; §5.9 de ese documento cubre
  bombas y *grazing*, hermanos de este sistema en otro género.
- [04 · 08 — Tower Defense](./08%20-%20Tower%20Defense.md) — *targeting* de torres
  (First/Last/Strongest/Closest) y proyectiles con *homing*.
- [04 · 23 — IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) —
  el movimiento (*Seek*/*Arrive*) que lleva a un enemigo hasta su punto de cobertura.
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — `global.a11y`, donde vive el
  interruptor de asistencia de puntería.
- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) —
  el mismo problema de "qué golpea y qué puede ser golpeado", resuelto para el cuerpo a
  cuerpo; `take_damage()` que este documento invoca sigue las mismas reglas.
- [04 · 31 — IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md) —
  dónde vive la decisión de *cuándo* buscar cobertura o disparar.
- [13 · 13 — Matemáticas aplicadas al juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
  `girar_hacia` (§3.2), `en_cono_vision` y `dot_product_normalised` (§2.4), `cortan_segmentos`
  (§6.5) y los límites de `collision_line` (§6.8) que este documento resuelve con
  `collision_line_list`.

---

## 9. Fuentes

- Manual oficial — `collision_line` —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/collision_line.htm
- Manual oficial — `collision_line_list` (es y en, contrastadas — la versión española dice
  "desde el centro de la línea", la inglesa "desde el **inicio** de la línea"; me he fiado de
  la inglesa) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/collision_line_list.htm
- Manual oficial — `ds_list_create` / listas DS —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Data_Structures/DS_Lists/ds_list_create.htm
- **Ultimate Guide To Collision Functions** (tutorial oficial; confirma que
  `collision_line_list` existe junto al resto de la familia `collision_*_list`, consultado con
  `curl` el 2026-09-06 tras el bloqueo del `User-Agent` por defecto) —
  https://gamemaker.io/tutorials/collision-functions
- Wikipedia — *Aim assist* (consultado 2026-09-06; términos "zoom snapping",
  "camera magnetism", "slowdown") — https://en.wikipedia.org/wiki/Aim_assist
- Wikipedia — *Cover system* (consultado 2026-09-06; *Kill.Switch* 2003 y *Gears of War* 2006
  como hitos) — https://en.wikipedia.org/wiki/Cover_system
- Wikipedia — *Hitscan* (consultado 2026-09-06; definición y compensaciones frente a
  proyectil simulado) — https://en.wikipedia.org/wiki/Hitscan
- Wikipedia — *Recoil* (consultado 2026-09-06; solo la física real — conservación del
  momento— como fundamento de por qué el retroceso se siente "físico"; el artículo NO cubre
  recoil de videojuego, así que no se cita para nada de bloom/patrones) —
  https://en.wikipedia.org/wiki/Recoil
- `_indice/auditorias/combate-enemigos.md` — propuesta P3, el encargo de este documento.
